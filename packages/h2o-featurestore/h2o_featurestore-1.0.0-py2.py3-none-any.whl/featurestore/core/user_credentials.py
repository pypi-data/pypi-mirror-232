class AzureKeyCredentials:
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key


class AzureSasCredentials:
    def __init__(self, account_name, sas_token):
        self.account_name = account_name
        self.sas_token = sas_token


class AzurePrincipalCredentials:
    def __init__(self, account_name, client_id, tenant_id, secret):
        self.account_name = account_name
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.secret = secret


class S3Credentials:
    def __init__(self, access_key, secret_key, region=None, endpoint=None, role_arn=None):
        self.access_token = access_key
        self.secret_token = secret_key
        self.region = region
        self.role_arn = role_arn
        self.endpoint = endpoint


class SnowflakeCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class SnowflakeKeyPairCredentials:
    def __init__(self, user, private_key_file, passphrase=None):
        self.user = user
        self.private_key_file = private_key_file
        self.passphrase = passphrase


class TeradataCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class PostgresCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class MongoDbCredentials:
    def __init__(self, user, password):
        self.user = user
        self.password = password
