from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient, PyJWTError

from app.core.config import get_settings


ALLOWED_SIGNING_ALGORITHMS = ["ES256", "RS256"]


class IdentityVerificationError(Exception):
    pass


@dataclass(frozen=True)
class VerifiedIdentity:
    issuer: str
    subject: str
    email: str | None


class IdentityProvider:
    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
    ) -> None:
        self.issuer = issuer.rstrip("/")
        self.audience = audience
        self.jwks_client = PyJWKClient(
            f"{self.issuer}/.well-known/jwks.json",
            cache_jwk_set=True,
            lifespan=600,
            timeout=5,
        )

    def verify_token(self, token: str) -> VerifiedIdentity:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=ALLOWED_SIGNING_ALGORITHMS,
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "require": ["iss", "sub", "aud", "exp", "iat"],
                },
            )
        except PyJWTError as error:
            raise IdentityVerificationError(
                "Identity token is invalid"
            ) from error

        subject = claims.get("sub")
        email = claims.get("email")

        if not isinstance(subject, str) or not subject:
            raise IdentityVerificationError(
                "Identity token has no valid subject"
            )

        if email is not None and not isinstance(email, str):
            raise IdentityVerificationError(
                "Identity token has no valid email"
            )

        return VerifiedIdentity(
            issuer=self.issuer,
            subject=subject,
            email=email,
        )


@lru_cache
def get_identity_provider() -> IdentityProvider:
    settings = get_settings()

    return IdentityProvider(
        issuer=settings.identity_provider_issuer,
        audience=settings.identity_provider_audience,
    )
