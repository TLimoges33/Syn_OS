# Branch Cleanup Strategy

## Current Repository Status

### Primary Repositories
- **TLimoges33/Syn_OS-Dev-Team** (Development workspace)
- **TLimoges33/Syn_OS** (Main project repository)
- **TLimoges33/SynOS** (Legacy/alternative)
- **TLimoges33/SynapticOS** (Legacy/alternative)

### Target Branch Alignment

All repositories should maintain these 3 core branches:

1. **`main`** - Primary development branch
   - Target SHA: `d43122b3` (current main)
   - Purpose: Main development integration

2. **`master`** - Production stable branch  
   - Target SHA: `97b9be98` (current master)
   - Purpose: Production releases

3. **`dev-team`** - Feature development branch
   - Target SHA: `19c6e411` (latest with clean structure)
   - Purpose: Team feature development and testing

## Cleanup Actions Needed

### 1. Branch Synchronization
- [ ] Align all repos to target SHAs above
- [ ] Create missing core branches where needed
- [ ] Update existing branches to target commits

### 2. Stale Branch Cleanup
Identify and remove:
- `feature/*` branches older than 30 days
- `hotfix/*` branches that have been merged
- `chore/*` temporary branches
- `extract/*` migration branches
- Duplicate `dev-*` variants
- Old `staging` branches

### 3. Branch Protection Rules
- [ ] Protect `master` branch (production)
- [ ] Protect `main` branch (development)
- [ ] Allow `dev-team` to be force-pushable for development workflow

## Implementation Steps

1. **Phase 1: Core Branch Alignment**
   ```bash
   ./scripts/cleanup_all_branches.sh
   ```

2. **Phase 2: Stale Branch Removal**
   ```bash
   ./scripts/remove_stale_branches.sh
   ```

3. **Phase 3: Protection Setup**
   ```bash
   ./scripts/setup_branch_protections.sh
   ```

## Expected Outcomes

- **Simplified branch structure** across all repositories
- **Consistent SHA alignment** for core branches
- **Faster development workflow** with clean branch list
- **Better team coordination** with standardized branches

## Repository Size Benefits

Cleaning up stale branches will:
- Reduce repository metadata overhead
- Improve GitHub UI performance
- Speed up clone/fetch operations
- Simplify branch selection in Codespaces

## Next Steps

1. Complete current push of cleaned repository structure
2. Execute branch cleanup script across all repositories
3. Verify branch alignment and test development workflow
4. Document new branch strategy for team use
