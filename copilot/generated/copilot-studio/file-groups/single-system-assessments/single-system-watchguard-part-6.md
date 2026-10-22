# Single-System Analysis — WatchGuard (Run Card part 6)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-watchguard` run card part 6: continuation of `single-system-watchguard run card` with metrics P025-P029. Run each line exactly as step 4 of the main run card says.

### single-system-watchguard metrics P025-P029

- **P025** metricId 599 - Quota Rule Summary (array)
  - fallback query: `` QuotaRules[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Action`, to_string(Action)]), join(`: `, [`Status`, to_string(Status)])]) | sort(@) ``
- **P026** metricId 2001 - Serial Number (string)
  - fallback query: `SystemInfo.SerialNumber`
- **P027** metricId 607 - Site-to-Site Phase 1 Policy Summary (array)
  - fallback query: `` SiteToSiteVPN.Phase1[].join( `, `, [join(`: `, [`Policy Name`, to_string(PolicyName)]), join(`: `, [`Status`, to_string(Status)]), join(`: `, [`Version`, to_string(Version)]), join(`: `, [`Peer Name`, to_string(PeerName)]), join(`: `, [`Action Name`, to_string(ActionName)]), join(`: `, [`Xchng Mode`, to_string(XchngMode)]), join(`: `, [`Local Interface`, to_string(LocalInterface)]), join(`: `, [`VIF`, to_string(VIF)]), join(`: `, [`VIF Protocol`, to_string(VIFProto)])]) | sort(@) ``
- **P028** metricId 608 - Site-to-Site Phase 2 Policy Summary (array)
  - fallback query: `` SiteToSiteVPN.Phase2[].join( `, `, [join(`: `, [`Policy Name`, to_string(PolicyName)]), join(`: `, [`Status`, to_string(Status)]), join(`: `, [`IKE Version`, to_string(IKEVersion)]), join(`: `, [`Mode`, to_string(Mode)]), join(`: `, [`Key Mode`, to_string(KeyMode)]), join(`: `, [`VPN Type`, to_string(VPNType)]), join(`: `, [`IKE Policy`, to_string(IKEPolicyName)])]) | sort(@) ``
- **P029** metricId 604 - Single-User Account Summary (array)
  - fallback query: `` Users[?Type EQ_OP 'Single-User'].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`AuthServer`, to_string(AuthServer)]), join(`: `, [`Description`, to_string(Description)])]) | sort(@) ``
