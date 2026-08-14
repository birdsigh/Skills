---
name: commit-and-push
description: Safely review, verify, commit, and push intended repository changes to an established upstream branch. Use when the user invokes /commit-and-push, asks to commit and push current work, or requests publishing completed changes without creating a pull request.
---

# Commit and push

Review, verify, commit, and push the intended changes. Preserve unrelated work and require explicit approval before every push.

## Safety rules

- Read and follow all applicable repository instructions before acting.
- Never assume every worktree change belongs to the current task.
- Never discard, reset, restore, stash, overwrite, or otherwise alter unrelated changes.
- Treat the existing index as user-owned state. Never alter pre-existing staging without explicit confirmation.
- Never bypass Git hooks or verification with `--no-verify`.
- Never pull, merge, rebase, amend, reset, force-push, or retry a rejected push as part of this workflow.
- Never infer or create an upstream branch.
- Never expose secret values when describing files or failures.
- Treat the original invocation as permission to prepare a commit, not permission to push.
- Require explicit confirmation immediately before every push.

## 1. Inspect the repository

Determine:

- the repository root;
- all applicable repository instructions;
- the current branch;
- the configured upstream branch and remote;
- the remote default branch;
- whether HEAD is detached;
- whether a merge, rebase, cherry-pick, revert, or conflict is in progress;
- all modified, deleted, renamed, staged, and untracked paths.

Stop and report without staging, committing, or pushing when:

- HEAD is detached;
- conflicts or an in-progress Git operation exist;
- the current branch has no configured upstream;
- the intended change ownership cannot be determined safely.

When no upstream is configured, report the current branch and available remote names without printing potentially credential-bearing URLs. Do not run `git push -u` or create a remote branch.

## 2. Fetch and inspect existing outgoing commits

Fetch the configured upstream remote before calculating outgoing commits. Fetch only: do not pull, merge, rebase, or prune.

If fetch fails, stop and report that the outgoing range cannot be verified reliably. Do not rely silently on stale remote-tracking refs.

Compare HEAD with the refreshed configured upstream and calculate both ahead and behind counts.

- If HEAD and the upstream have diverged, stop and report both counts.
- If HEAD is only behind the upstream, stop and report that synchronization is required.
- Do not pull, merge, or rebase to reconcile either state.

Before doing any other work, identify every commit and file already waiting to be pushed.

If existing outgoing commits are present, show:

- the upstream destination;
- every outgoing commit SHA and subject;
- every changed file when the outgoing range contains 50 files or fewer;
- aggregate insertion and deletion counts;
- a warning that these commits will be included in any later push.

Ask whether those existing commits should be included. Wait for confirmation. This confirmation permits the workflow to continue; it does not authorize a push.

If the existing outgoing range contains more than 50 files, use the large-change gate below instead of printing every filename.

If the worktree is clean and outgoing commits exist, skip commit preparation and proceed to the final outgoing-range review. If the worktree is clean and there are no outgoing commits, stop and report that there is nothing to commit or push.

## 3. Apply the large-change gate

Apply this gate separately to each changed-path set reviewed by the workflow: the existing outgoing range, the worktree, and the final outgoing range. Count logical paths, treating a rename as one path change.

When the count exceeds 50, stop and show:

- which changed-path set triggered the gate;
- total path count;
- counts of added/untracked, modified, deleted, and renamed paths;
- counts grouped by top-level directory or another concise, coherent area;
- whether the breadth appears consistent with one change.

Ask whether to continue reviewing that large change set. For the worktree gate, wait for confirmation before staging or running potentially expensive verification. Approval of any large-change gate does not authorize a push.

## 4. Resolve the commit scope

Account for every changed and untracked path. Inspect enough of each diff or file to determine what it appears to concern.

Treat paths staged before this workflow as user-owned staging. If a pre-staged path would be excluded or its ownership is ambiguous, stop and ask whether to keep it included or explicitly unstage it. Never change pre-existing staging silently.

Separate paths into:

- intended changes to commit;
- changes that appear unrelated, local-only, generated unexpectedly, suspicious, or otherwise unsuitable to commit.

If any path would be left uncommitted, show:

- each excluded path;
- its status;
- a brief, non-sensitive description of what it appears to concern;
- why it appears separate from the intended commit.

Ask whether to leave those paths out, include them, or revise the selection. Wait for confirmation before staging.

Do not mention ordinary ignored files unless they are suspiciously relevant to the requested work.

If no intended uncommitted changes remain but confirmed outgoing commits exist, skip verification, staging, and commit creation unless repository instructions require otherwise. Proceed to the final outgoing-range review. If neither intended changes nor outgoing commits remain, stop and report that there is nothing to commit or push.

## 5. Verify the intended changes

Run the smallest relevant verification required by repository instructions or clearly implied by the changed files.

- Prefer focused tests, lint, or typechecks over repository-wide suites.
- Do not duplicate checks that repository instructions explicitly assign to commit hooks.
- If no separate verification is appropriate, state that none was run; configured Git hooks will still run.
- If verification fails, stop before committing and report the useful failure output.
- Do not change code merely to silence an unrelated failure.

## 6. Stage and review

Stage only the confirmed intended paths. Do not use blanket staging when unrelated changes exist.

Review the staged name/status summary and staged patch. Confirm that:

- every staged change belongs to the intended work;
- no confirmed exclusion is staged;
- no credential, secret, suspicious large file, or unrelated generated artifact is included;
- the staged change is coherent enough for one commit.

If the staged scope differs materially from the confirmed scope, stop and explain the difference.

## 7. Generate and create the commit

Inspect recent commit subjects and follow the repository's established convention. Generate a concise message from the staged diff:

- use an imperative subject;
- keep the subject at most 72 characters with no trailing period;
- capture the primary user-visible or developer-visible change;
- use a short body only when it adds useful context.

Commit normally so all configured Git hooks run.

If verification, `git commit`, or a Git hook fails:

- stop immediately;
- report the hook or command that failed, when identifiable;
- show useful error or test output without leaking secrets;
- inspect and report whether a commit was created;
- leave staged and unstaged changes intact;
- do not retry with `--no-verify`;
- do not proceed to push.

## 8. Recalculate the complete outgoing push

Fetch the configured upstream remote again immediately before calculating the final outgoing range. If the fetch fails, stop and report that the range cannot be verified reliably.

Compare HEAD with the newly refreshed upstream and recalculate ahead and behind counts. If the upstream is now ahead or has diverged, stop before presenting a push confirmation. Do not reconcile automatically.

Calculate the complete outgoing range. It must include pre-existing outgoing commits as well as any newly created commit.

Determine:

- every outgoing commit;
- every file added, modified, deleted, or renamed by the complete outgoing range;
- aggregate insertion and deletion counts;
- the exact destination remote and branch;
- the exact non-force push command, expressed explicitly as `git push <remote> HEAD:<remote-branch>` rather than relying on `push.default` or other destination inference.

If the complete outgoing range now exceeds 50 files and that exact breadth was not already approved, apply the large-change gate again. Do not print an unbounded filename list; summarize it by status and coherent directory or area, then wait for confirmation to continue.

## 9. Present the push summary

Before every push, show a concise summary containing:

- destination remote and branch;
- every outgoing commit SHA and subject;
- every changed filename when there are 50 files or fewer;
- for each file, whether it is added, modified, deleted, or renamed;
- aggregate file, insertion, and deletion counts;
- verification performed;
- every path deliberately left uncommitted and what it appears to concern;
- the exact push command.

If the destination is the detected remote default branch, display a prominent warning that the push goes directly to the default branch.

Ask: **Push these changes?** Wait for an explicit affirmative response. Neither the original invocation nor any earlier scope confirmation authorizes the push.

If confirmation is declined, leave the commit local and report that nothing was pushed.

## 10. Push once

After explicit confirmation, run the previously displayed push command against the configured upstream. Never force-push.

If the push fails or is rejected:

- stop immediately;
- report the remote error and resulting repository state;
- leave local commits intact;
- do not pull, merge, rebase, reset, amend, retry, or force-push;
- report that the attempted changes were not published.

If the push succeeds, report:

- pushed branch and remote;
- commit SHA and subject for each pushed commit;
- verification performed;
- any changes deliberately left uncommitted.