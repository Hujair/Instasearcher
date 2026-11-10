# Insta Searcher

## Updates

Run the app from a Git clone with Git installed and a configured upstream branch.
The header checks the tracked branch for new commits on startup. Choose **Update**
to install a fast-forward update, then restart the app. Active searches, modified
tracked files, divergent branches, and conflicting untracked or ignored files block
the update; resolve these manually before retrying.

The update check fetches commits from the configured upstream. It does not push
your changes. If an update changes dependencies, install those dependencies
before restarting.
