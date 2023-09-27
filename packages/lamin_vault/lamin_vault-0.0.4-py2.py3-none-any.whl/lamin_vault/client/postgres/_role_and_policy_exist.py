def role_and_policy_exist(vault_client, instance_id, account_id):
    role_name = f"{instance_id}-{account_id}-db"
    policy_name = f"{role_name}-policy"

    role_exists = vault_client.secrets.database.read_role(name=role_name) is not None
    policy_exists = vault_client.sys.read_policy(name=policy_name) is not None

    return role_exists and policy_exists
