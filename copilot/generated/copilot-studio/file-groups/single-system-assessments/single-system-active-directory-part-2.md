# Single-System Analysis — Active Directory (Run Card part 2)

Recipe `single-system-active-directory` run card part 2: continuation of `single-system-active-directory run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-active-directory metrics P001-P006

- **P001** metricId none - DHCP Server Scopes (array) - Returns null when DC does not host the DHCP role. Check for null before attempting array operations. DHCP.Serverv4Scopes[0] confirmed null on 4 test systems — f...
  - fallback query: `DHCP.Serverv4Scopes`
- **P002** metricId 780 - Default Guest Account Enabled (boolean)
  - fallback query: `DefaultGuestAccountEnabled`
- **P003** metricId 781 - Guest Members Count (integer) - Recipe uses length(GuestMembers) — equivalent to GuestMembers | length(@). Global metric id=781 uses the pipe form; both evaluate identically.
  - fallback query: `GuestMembers | length(@)`
- **P004** metricId 796 - Account Lockout Duration (integer) - Unit is hours as a float. 0.25 = 15 min, 0.5 = 30 min. Do NOT interpret as minutes.
  - fallback query: `AccountPolicy.AccountLockoutDuration`
- **P005** metricId 795 - Account Lockout Observation Window (integer) - Unit is hours as a float, same as AccountLockoutDuration.
  - fallback query: `AccountPolicy.AccountLockoutObservationWindow`
- **P006** metricId 794 - Account Lockout Threshold (integer) - 0 = no lockout enforced. Validated: System A returned 0 (lockout disabled).
  - fallback query: `AccountPolicy.lockoutThreshold`
