"""
Manage your website's ownership details.

"""

import os
import pathlib
import subprocess
from base64 import b64encode
from hashlib import sha256
from urllib.parse import urlparse

import httpsig
import requests
import requests.auth
import web
from web import tx

app = web.application(
    __name__,
    prefix="owner",
    model={
        "identities": {
            "created": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "card": "JSON",
        },
        "passphrases": {
            "created": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "passphrase_salt": "BLOB",
            "passphrase_hash": "BLOB",
        },
    },
)


def ap_request(url, data=None):
    headers = {
        "Accept": "application/activity+json",
        "Date": web.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Digest": f"SHA-256={b64encode(sha256(data or b'').digest()).decode()}",
    }
    auth = HTTPSignatureAuth(
        f"{tx.origin}/owner/actor#main-key",
        ap_pvtkey.open("r").read(),
        algorithm="rsa-sha256",
        headers=("Date", "Host", "Digest", "(request-target)"),
        sign_header="signature",
    )
    return requests.get(url, headers=headers, auth=auth).json()


class HTTPSignatureAuth(requests.auth.AuthBase):
    def __init__(
        self,
        key_id="",
        secret="",
        algorithm=None,
        headers=None,
        sign_header="authorization",
    ):
        headers = headers or []
        self.header_signer = httpsig.sign.HeaderSigner(
            key_id=key_id,
            secret=secret,
            algorithm=algorithm,
            headers=headers,
            sign_header=sign_header,
        )
        self.uses_host = "host" in [h.lower() for h in headers]

    def __call__(self, r):
        headers = self.header_signer.sign(
            r.headers,
            host=urlparse(r.url).netloc if self.uses_host else None,
            method=r.method,
            path=r.path_url,
        )
        r.headers.update(headers)
        return r


@app.query
def get_identities(db):
    """Return identity with given `uid`."""
    return db.select("identities")


@app.query
def get_identity(db, uid="/"):
    """Return identity with given `uid`."""
    return db.select(
        "identities",
        where="json_extract(identities.card, '$.uid[0]') = ?",
        vals=[uid],
    )[0]


@app.query
def update_details(db, name=None, photo=None, nickname=None, note=None, uid="/"):
    """Update name of identity with given `uid`."""
    card = db.select(
        "identities",
        where="json_extract(identities.card, '$.uid[0]') = ?",
        vals=[uid],
    )[0]["card"]
    if name:
        card["name"] = [name]
    if photo:
        card["photo"] = [photo]
    if nickname:
        card["nickname"] = [nickname]
    if note:
        card["note"] = [note]
    db.update(
        "identities",
        card=card,
        where="json_extract(identities.card, '$.uid[0]') = ?",
        vals=[uid],
    )


@app.query
def add_identity(db, name, uid="/"):
    """Create an identity."""
    db.insert("identities", card={"uid": [uid], "name": [name]})


@app.query
def get_passphrase(db):
    """Return most recent passphrase."""
    try:
        return db.select("passphrases", order="created DESC")[0]
    except IndexError:
        return {}


@app.query
def update_passphrase(db):
    """Update the passphrase."""
    passphrase_salt, passphrase_hash, passphrase = web.generate_passphrase()
    db.insert(
        "passphrases",
        passphrase_salt=passphrase_salt,
        passphrase_hash=passphrase_hash,
    )
    return passphrase


@app.wrap
def initialize_owner(handler, main_app):
    """Ensure an owner exists and add their details to the transaction."""
    try:
        tx.host.owner = app.model.get_identity()["card"]
    except IndexError:
        secret = web.form(secret=None).secret
        is_dev = os.getenv("WEBCTX") == "dev"
        if secret or is_dev:
            if main_app.cfg.get("SECRET") != secret and not is_dev:
                raise web.BadRequest("bad secret")
            app.model.add_identity("Unnamed")
            passphrase = " ".join(app.model.update_passphrase())
            tx.host.owner = tx.user.session = app.model.get_identity()["card"]
            tx.user.is_owner = True
            web.header("Content-Type", "text/html")
            raise web.Created(app.view.claimed(tx.origin, passphrase), tx.origin)
        raise web.NotFound("no identity initialized")
    tx.user.is_owner = tx.user.session.get("uid", [None])[0] == "/"
    yield


@app.wrap
def authorize_owner(handler, main_app):
    """Manage access to owner-only resources."""
    if not tx.user.is_owner and tx.request.method.lower() in getattr(
        handler, "owner_only", []
    ):
        raise web.Unauthorized(app.view.unauthorized())
    yield


@app.control("")
class Owner:
    """Owner information."""

    owner_only = ["get", "post"]

    def get(self):
        """Render site owner information."""
        return app.view.index()

    def post(self):
        """Update owner information."""
        form = web.form("name", "photo", "nickname", "note")
        app.model.update_details(form.name, form.photo, form.nickname, form.note)
        raise web.SeeOther("/owner")


@app.control(r"sign-in")
class SignIn:
    """Sign in as the owner of the site."""

    def get(self):
        """Verify a sign-in or render the sign-in form."""
        try:
            self.verify_passphrase()
        except web.BadRequest:
            if tx.user.is_owner:
                raise web.SeeOther("/")
            return_to = web.form(return_to="").return_to
            return app.view.signin(return_to)

    def post(self):
        """Verify a sign-in."""
        self.verify_passphrase()

    def verify_passphrase(self):
        """Verify passphrase, sign the owner in and return to given return page."""
        form = web.form("passphrase", return_to="")
        passphrase = app.model.get_passphrase()
        if web.verify_passphrase(
            passphrase["passphrase_salt"],
            passphrase["passphrase_hash"],
            form.passphrase.replace(" ", ""),
        ):
            tx.user.session = app.model.get_identity()["card"]
            raise web.SeeOther(f"/{form.return_to}")
        raise web.Unauthorized("bad passphrase")


@app.control("sign-out")
class SignOut:
    """Sign out while signed in as the owner of the site."""

    owner_only = ["get", "post"]

    def get(self):
        """Return the sign out form."""
        return app.view.signout()

    def post(self):
        """Sign the owner out and return to given return page."""
        tx.user.session = None
        return_to = web.form(return_to="").return_to
        raise web.SeeOther(f"/{return_to}")


@app.control("reset")
class Reset:
    """Reset the passphrase. You must manually delete the current passphrase first."""

    def get(self):
        """Return the new passphrase."""
        if not app.model.get_passphrase():
            return "Your new password: " + " ".join(app.model.update_passphrase())
        return "Passphrase must be manually deleted first."


ap_pubkey = pathlib.Path("ap_public.pem")
ap_pvtkey = pathlib.Path("ap_private.pem")


@app.control("actor")
class ActivityPubActor:
    """."""

    def get(self):
        """."""
        if not ap_pubkey.exists():
            subprocess.run(["openssl", "genrsa", "-out", ap_pvtkey, "2048"])
            subprocess.run(
                [
                    "openssl",
                    "rsa",
                    "-in",
                    ap_pvtkey,
                    "-outform",
                    "PEM",
                    "-pubout",
                    "-out",
                    ap_pubkey,
                ]
            )
        with ap_pubkey.open() as fp:
            pubkey = fp.read().strip()
        web.header("Content-Type", "application/ld+json")
        profile = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": f"{tx.origin}/owner/actor",
            "url": [f"{tx.origin}"],
            "type": "Person",
            "preferredUsername": tx.host.owner["nickname"][0],
            "name": tx.host.owner["name"][0],
            "summary": tx.host.owner["note"][0],
            "inbox": f"{tx.origin}/inbox",
            "publicKey": {
                "id": f"{tx.origin}/owner/actor#main-key",
                "owner": f"{tx.origin}/owner/actor",
                "publicKeyPem": pubkey,
            },
        }
        card = app.model.get_identity()["card"]
        if photo := card.get("photo"):
            profile["icon"] = [{"type": "Image", "url": f"{tx.origin}/{photo}"}]
        return profile


@app.control(".well-known/webfinger", prefixed=False)
class WebfingerProfile:
    """."""

    def get(self):
        """."""
        web.header("Content-Type", "application/jrd+json")
        return {
            "subject": f"acct:{tx.host.owner['nickname'][0]}@{tx.host.name}",
            "aliases": [tx.origin],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": tx.origin,
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"{tx.origin}/owner/actor",
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template": f"{tx.origin}/subscriptions?uri={{uri}}",
                },
            ],
        }
