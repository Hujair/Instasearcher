# Insta Searcher

## Updates

Run the app from a Git clone with Git installed and a configured upstream branch.
The header checks the tracked branch for new commits on startup. Choose **Update**
to install a fast-forward update, then restart the app. Active searches, modified
tracked files, divergent branches, and conflicting untracked or ignored files block
the update; resolve these manually before retrying.
The version shown comes from the most recent commit message beginning with a
version such as `0.1.0`. If none exists, the short Git commit ID is shown instead.
**modified** indicates tracked files have local changes. After an update, restart
to load the installed version.

The update check fetches commits from the configured upstream. It does not push
your changes. If an update changes dependencies, install those dependencies
before restarting.
