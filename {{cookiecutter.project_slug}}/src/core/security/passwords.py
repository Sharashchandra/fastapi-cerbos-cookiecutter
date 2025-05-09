import bcrypt


class Password:
    @classmethod
    def get_hashed_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password as a string.
        """
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(password.encode("utf-8"), salt)

        return password.decode("utf-8")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
