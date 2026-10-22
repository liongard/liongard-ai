# Single-System Analysis — WatchGuard (Run Card part 5)

Recipe `single-system-watchguard` run card part 5: continuation of `single-system-watchguard run card` with metrics P019-P024. Run each line exactly as step 4 of the main run card says.

### single-system-watchguard metrics P019-P024

- **P019** metricId 609 - Mobile IPSec Client VPN Policies (array)
  - fallback query: `` VPN.ClientVPN.MobileIPSec[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`AuthServer`, to_string(AuthServer)]), join(`: `, [`Allowed Access`, to_string(AllowedAccessStr_r)]), join(`: `, [`Virtual IP Address Pool`, to_string(VirtualIPAddressPool)]), join(`: `, [`Settings`, to_string(IPSecSettings)])]) | sort(@) ``
- **P020** metricId 610 - Mobile SSL VPN Settings Summary (object)
  - fallback query: `` VPN.ClientVPN.MobileSSL.join( `, `, [join(`: `, [`SSL Server`, to_string(SslServer)]), join(`: `, [`DNS Servers`, to_string(DnsServers)]), join(`: `, [`Domain Name`, to_string(DomainName)]), join(`: `, [`Encryption`, to_string(Encryption)]), join(`: `, [`VPN Traffic`, to_string(VpnTraffic)]), join(`: `, [`DataChannel`, to_string(DataChannel)]), join(`: `, [`IP Address Pool`, to_string(IpAddressPool)]), join(`: `, [`Authentication`, to_string(Authentication)]), join(`: `, [`Allowed Resources`, to_string(AllowedResources)]), join(`: `, [`Auth Users`, to_string(AuthenticationUsers)])]) ``
- **P021** metricId 2000 - Hardware Model (string)
  - fallback query: `SystemInfo.Model`
- **P022** metricId 597 - 1:1 NAT Summary (array)
  - fallback query: `` NAT.oneToOneNAT[].join( `, `, [join(`: `, [`Interface`, to_string(Interface)]), join(`: `, [`NAT Address`, to_string(NATAddress)]), join(`: `, [`Real Address`, to_string(RealAddress)])]) | sort(@) ``
- **P023** metricId 320 - Physical Interface Count (integer)
  - fallback query: `SystemInfo.PhysicalInterface`
- **P024** metricId 600 - Quota Action Summary (array)
  - fallback query: `` QuotaAction[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Time(Min/Day)`, to_string(TimeInMinPerDay)]), join(`: `, [`Bandwidth(MB/Day)`, to_string(BandwidthInMBPerDay)])]) | sort(@) ``
