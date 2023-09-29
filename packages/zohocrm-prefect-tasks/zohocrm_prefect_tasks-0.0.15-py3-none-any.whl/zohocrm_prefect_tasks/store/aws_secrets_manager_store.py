import os
import json

from zcrmsdk.src.com.zoho.api.authenticator.store.token_store import TokenStore
from zcrmsdk.src.com.zoho.api.authenticator.oauth_token import OAuthToken, TokenType
from zcrmsdk.src.com.zoho.crm.api.util.constants import Constants
from zcrmsdk.src.com.zoho.crm.api.exception.sdk_exception import SDKException

from ..aws.secretsmanager_client import SecretsManagerClient


class AWSSecretsManagerStore(TokenStore):

    def __init__(self, secret_name=None):

        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_secret_name = secret_name or os.getenv('AWS_SECRETS_MANAGER_ZOHO_CRM_SECRET_NAME')
        self.aws_region = os.getenv('AWS_SECRETS_MANAGER_REGION')

        self.aws_secrets_manager_client = SecretsManagerClient.get_instance(
            access_key=self.aws_access_key,
            secret_key=self.aws_secret_key,
            region_name=self.aws_region
        )

        self.aws_secrets_manager_client.name = self.aws_secret_name

        self.headers = [Constants.USER_MAIL, Constants.CLIENT_ID, Constants.REFRESH_TOKEN, Constants.ACCESS_TOKEN, Constants.GRANT_TOKEN, Constants.EXPIRY_TIME]

    def get_token(self, user, token):
        """
        Parameters:
            user (UserSignature) : A UserSignature class instance.
            token (Token) : A Token (zcrmsdk.src.com.zoho.api.authenticator.OAuthToken) class instance
        """

        try:
            if isinstance(token, OAuthToken):
                tokens_list = []
                secret_strng = self.aws_secrets_manager_client.get_value()
                secrets_list = json.loads(secret_strng.get('SecretString'))
                for secret in secrets_list:
                    tokens_list.append(list(secret.values()))
                for row in tokens_list:
                    if len(row) == 0:
                        continue
                    if self.check_token_exists(user.email, token, row):
                        token.access_token = row[3]
                        token.expires_in = row[5]
                        token.refresh_token = row[2]
                        return token

        except IOError as ex:
            raise SDKException(code=Constants.TOKEN_STORE, message=Constants.GET_TOKEN_FILE_ERROR, cause=ex)

        return None

    def save_token(self, user, token):
        """
        Parameters:
            user (UserSignature) : A UserSignature class instance.
            token (Token) : A Token (zcrmsdk.src.com.zoho.api.authenticator.OAuthToken) class instance
        """

        """
        secret_string = self.aws_secrets_manager_client.get_value()
        secrets = json.loads(secret_string.get('SecretString'))
        lines = []
        for obj in secrets:
            lines.append(list(obj.values()))
        """
        lines = []

        if isinstance(token, OAuthToken):
            token.user_mail = user.email
            self.delete_token(token)
            try:

                token_list = [user.email, token.client_id, token.refresh_token, token.access_token, token.grant_token, token.expires_in]
                lines.append(token_list)
                print('Saving token')

                new_secret = [dict(zip(self.headers, line)) for line in lines]
                self.aws_secrets_manager_client.put_value(json.dumps((new_secret)))

            except IOError as ex:
                raise SDKException(code=Constants.TOKEN_STORE, message=Constants.SAVE_TOKEN_FILE_ERROR, cause=ex)

    def delete_token(self, token):
        """
        Parameters:
            token (Token) : A Token (zcrmsdk.src.com.zoho.api.authenticator.OAuthToken) class instance
        """

        if isinstance(token, OAuthToken):
            try:
                tokens_list = []
                secret_strng = self.aws_secrets_manager_client.get_value()
                secrets_list = json.loads(secret_strng.get('SecretString'))
                for secret in secrets_list:
                    tokens_list.append(list(secret.values()))
                for row in tokens_list:
                    if len(row) == 0:
                        continue
                    if self.check_token_exists(token.user_mail, token, row):
                        tokens_list.remove(row)

                new_secret = [dict(zip(self.headers, line)) for line in tokens_list]
                self.aws_secrets_manager_client.put_value(json.dumps(new_secret))

            except IOError as ex:
                raise SDKException(code=Constants.TOKEN_STORE, message=Constants.DELETE_TOKEN_FILE_ERROR, cause=ex)

    def get_tokens(self):
        """
        Returns:
            list: List of stored tokens
        """

        tokens = []

        try:
            secret_string = self.aws_secrets_manager_client.get_value()
            secrets = json.loads(secret_string.get('SecretString'))
            for secret in secrets:
                if len(list(filter(None, secret))) == 0:
                    continue
                row = list(secret.values())
                token_type = TokenType.REFRESH if len(row[4]) == 0 else TokenType.GRANT
                token_value = row[4] if token_type == TokenType.GRANT else row[2]
                token = OAuthToken(row[1], None, token_value, token_type)
                token.user_mail = row[0]
                token.expires_in = row[5]
                token.access_token = row[3]
                tokens.append(token)

            return tokens
        except Exception as ex:
            raise SDKException(code=Constants.TOKEN_STORE, message=Constants.GET_TOKENS_FILE_ERROR, cause=ex)

    def delete_tokens(self):
        tokens = []
        try:
            self.aws_secrets_manager_client.put_value(json.dumps(tokens))
        except Exception as ex:
            raise SDKException(code=Constants.TOKEN_STORE, message=Constants.DELETE_TOKENS_FILE_ERROR, cause=ex)

    def check_token_exists(self, email, token, row):
        if email is None:
            raise SDKException(Constants.USER_MAIL_NULL_ERROR, Constants.USER_MAIL_NULL_ERROR_MESSAGE)

        client_id = token.client_id
        grant_token = token.grant_token
        refresh_token = token.refresh_token
        token_check = grant_token == row[4] if grant_token is not None else refresh_token == row[2]

        if row[0] == email and row[1] == client_id and token_check:
            return True

        return False























