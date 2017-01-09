# Vault playbook

The `vault.yml` playbook handles your entire [Ansible Vault](https://roots.io/trellis/docs/vault/) setup.
* detects or creates a `vault_password_file` entry in `ansible.cfg`
* uses your existing vault password file or creates one if missing
* encrypts `vault.yml` files
* saves backups of `vault.yml` files before changing them
* builds `vault_users` to include all `users`
* builds `vault_wordpress_sites` to include all `wordpress_sites`
* retains your existing `vault.yml` variables/values, whether default or custom (optionally recreates values)
* creates missing portions of `vault.yml` files, using random passwords, salts, and keys

On a new or existing project, add your `wordpress_sites` and `users` then run this playbook to generate any users, sites, passwords, salts, or keys that are missing from `vault.yml` files. The playbook also generates missing `vault.yml` files.
```
ansible-playbook vault.yml
```

You may replace all default `vault.yml` variables with fresh random values (e.g., on a new project).
```
ansible-playbook vault.yml -e vault_overwrite_default_vars=true
```

The playbook runs for all environments by default, but you may specify a specific environment if you wish.
```
ansible-playbook vault.yml -e env=production
```

You may invoke the options below by defining the indicated variables in your `group_vars` files.

## `vault.yml` variables

You may manually edit the `vault.yml` files at any time. Re-running the `vault.yml` playbook will retain all validly formatted variables/values (whether default or custom) except as affected by your adjustments to any relevant options below. Custom comments will never be retained unless added to the templates in `roles/vault/templates`.

### Random strings

WP env salts/keys (66 chars) and passwords (15 chars) are created as random strings based on a shell command run on your local machine. You may customize the command:
```
random_string_cmd: head -c 500 /dev/urandom | perl -pe 'tr/A-Za-z0-9_!@#$%^&*()[]+={}|<>?:;.`-//dc;' | fold -w 66 | head -n 1
```

### Password length

You may customize the length of passwords.
```
vault_passwords_length: 15   # default: 15
```

### Recreate values

You may recreate any specific default variable by deleting its key and value(s) and re-running the playbook.

To recreate `vault.yml` files completely, delete the file(s) and run the `vault.yml` playbook. Alternatively, you may retain your custom variables in `vault.yml` files but overwrite Trellis default variables with fresh values.
```
vault_overwrite_default_vars: true   # default: false
```
Caution! Defining the above in a variable would risk overwriting your default variables every time you run the `vault.yml` playbook. It would be safer to leave the default variable `false` but specify the variable as `true` one time only via the CLI `extra-vars` option.
```
ansible-playbook vault.yml -e vault_overwrite_default_vars=true
```

Be cautious when changing passwords for servers that have already been provisioned. For example, if you have already set up a mysql database and want to change `vault_mysql_root_password`, you could use this `vault.yml` playbook to generate a new password, but then you would need to manually update the password on the server (vs. just rerunning the `server.yml` playbook with this new password).

### Sites

You may purge `vault_wordpress_sites` of sites that are no longer in `wordpress_sites`.
```
vault_remove_old_sites: true   # default: false
```

### Users

You may purge `vault_users` of users that are no longer in `users`.
```
vault_remove_old_users: true   # default: false
```

### Raw values

If you wrap a `vault.yml` variable value in `{% raw %}`, you will notice that this playbook strips off the `{% raw %}`. Instead of using `{% raw %}` to prevent a variable value from being templated, just add the variable to the `raw_vars` list in `group_vars/all/main.yml`. Then the variable's value will be wrapped in `{% raw %}` automatically behind the scenes.

## `vault.yml` files

### Encryption

The playbook will encrypt `vault.yml` files by default, but you may specify `decrypted`.
```
vault_files_state: decrypted   # default: encrypted
```

There are simple [vault commands](https://roots.io/trellis/docs/vault/#other-vault-commands) for working with encrypted `vault.yml` files.
```
ansible-vault view <file>
ansible-vault edit <file>
```

### `vault.yml` file mode

You may customize the mode of `vault.yml` files.
```
vault_files_mode: 0600   # default: 0600
```

### `vault.yml` file backups

Your old `vault.yml` files are backed up automatically. You may indicate the path for backups.
```
vault_backups_path: vault-backups   # default: vault-backups
```
The backups path will be added to `.gitignore` automatically.

You may disable automatic backup of `vault.yml` files.
```
vault_file_backups: false   # default: true
```
Disabling automatic backups will not delete existing backups.

## Vault password file

### Password file name

Your vault password file will be whatever file name/path you have set in your `ansible.cfg` under `[defaults]`. The playbook will add this line to your `ansible.cfg` if the line is missing.
```
# ansible.cfg
[defaults]
vault_password_file = .vault_pass
```
The vault password file name will be added to `.gitignore` automatically.

### Password file content

If the vault password file exists, its password will be used. Otherwise, the file will be created with a random password.

### Password file mode

You may customize the vault password file mode.
```
vault_password_file_mode : 0600   # default: 0600
```

### Disable password file feature

This playbook's vault password file tasks will automatically skip if you define `vault_files_state: decrypted` or if you run the playbook with the `--ask-vault-pass` CLI option.

You may manually force the vault password file tasks to skip.
```
vault_password_file_enabled: false   # default: true
```
This will not delete a vault password file that already exists, nor will it remove `vault_password_file` from `ansible.cfg`.
