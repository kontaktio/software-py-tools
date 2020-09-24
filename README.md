# software-py-tools
Useful code snippets to get rid of toil with automation.
* `delete_entities.py` - wipe entities and entity types from any Apps API account.
* `import_entities.py` - imports beacon entities into Apps API: can be imported from
IM API database directly or a CSV list of `uniqueId,mac` pairs.
* `apps_api_update_password.py` and `im_api_update_password.py` - set any new password
for any Apps API or IM API user. You only need to know user's email for that.
* `update_datahost_pl.py` - send configuration updates to multiple Portal Lights,
 e.g. all PLs from some account.

## Setting up
Requirements:
* Python 3.6+
* [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/)

### Console based setup
```sh
pipenv install
```

### PyCharm based setup
Pycharm natively supports Pipenv, so the setup procedure
is more intuitive - pick "Pipenv environment" in "Add interpeter"
dialog and assign the new interpreter to this project.

Then create Python Run configuration in order to run any
of the scripts.

## Running the code
* [.env file](https://pipenv-fork.readthedocs.io/en/latest/advanced.html#automatic-loading-of-env)
has to be created in top-level directory with all secrets
(e.g. DB passwords) defined in it. You can copy *sample.env*
as a template.
* Look at the `__main__` method in one of the top-level Python files.
Code should be self explanatory, adjust as needed and run it:
```sh
pipenv run python anything_you_want.py
# or Run the same file in PyCharm.
```

Command line arguments are not implemented intentionally for greater
flexibility.