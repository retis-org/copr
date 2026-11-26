Name:		retis
Version:	1.7.2
Release:	0%{?dist}
Summary:	Tracing packets in the Linux networking stack, using eBPF and interfacing with control and data paths such as OvS or Netfilter.
License:	GPLv2

URL:		https://github.com/retis-org/retis
Source:		https://github.com/retis-org/retis/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:		retis-fixes.diff
Patch1:		retis-rawhide-bpf.diff

%global rustup_env source $HOME/.cargo/env

BuildRequires:	clang
BuildRequires:	curl
BuildRequires:	elfutils-libelf-devel
BuildRequires:	jq
BuildRequires:	libpcap-devel
BuildRequires:	llvm
BuildRequires:	make
BuildRequires:	python3-devel
BuildRequires:	zlib-devel

%description
Tracing packets in the Linux networking stack, using eBPF and interfacing with control and data paths such as OpenVSwitch.

%prep
%autosetup -n %{name}-%{version} -p1
%{__mkdir} -p .cargo
cat > .cargo/config.toml << EOF
[profile.release]
opt-level = 3
debug = 2
strip = "none"

[env]
CFLAGS = "%{build_cflags}"
CXXFLAGS = "%{build_cxxflags}"
LDFLAGS = "%{build_ldflags}"

[install]
root = "%{buildroot}%{_prefix}"

[term]
verbose = true
EOF
RUSTUP_INIT_SKIP_PATH_CHECK=y curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -qy
# Pre-install rust-src: cc >= 1.4.0 invokes rustc via the rustup shim,
# causing parallel build.rs scripts to race on the component download.
$HOME/.cargo/bin/rustup component add rust-src

%build
%{rustup_env}
%if 0%{?rhel} == 8
/usr/bin/env CARGO_HOME=.cargo CARGO_CMD_OPTS="--no-default-features" make %{?_smp_mflags} release
%else
/usr/bin/env CARGO_HOME=.cargo make %{?_smp_mflags} release
%endif

%install
%{rustup_env}
%if 0%{?rhel} == 8
/usr/bin/env CARGO_HOME=.cargo CARGO_INSTALL_OPTS="--no-track --no-default-features" CARGO_CMD_OPTS="--no-default-features" make %{?_smp_mflags} install
%else
/usr/bin/env CARGO_HOME=.cargo CARGO_INSTALL_OPTS="--no-track" make %{?_smp_mflags} install
%endif
install -m 0755 -d %{buildroot}%{_datadir}/retis/profiles
install -m 0644 retis/profiles/* %{buildroot}%{_datadir}/retis/profiles

%check
%{rustup_env}
# Build of the test binary fails for some reason on copr [E0786].
# Disable the testing part for now, should be reverted later.
# Not a huge deal since we already test in our CI; but not perfect either.
%if 0
/usr/bin/env CARGO_HOME=.cargo make %{?_smp_mflags} test
%endif

%files
%license retis/LICENSE
%doc README.md
%{_bindir}/retis
%{_datadir}/retis/profiles

%changelog
* Tue Nov 26 2026 Paolo Valerio <pvalerio@redhat.com> - 1.7.2-0
- Fix context in retis-fixes.diff.
- Bump to 1.7.2.

* Tue Nov 24 2026 Paolo Valerio <pvalerio@redhat.com> - 1.7.1-0
- Bump to 1.7.1.

* Mon Aug 10 2026 Paolo Valerio <pvalerio@redhat.com> - 1.7.0-0
- Bump to 1.7.0.
- Fix patch context for retis-fixes.diff and retis-rawhide-bpf.diff.
- Pre-install rust-src to avoid a rustup race condition with cc >= 1.4.0 in parallel builds.
- Rename .cargo/config to .cargo/config.toml to silence deprecation warning.
- Fix c8s build by using rustup consistently for cargo/rustc/rustdoc
  via source $HOME/.cargo/env.

* Tue Feb 17 2026 Antoine Tenart <atenart@redhat.com> - 1.6.4-0
- Bump to 1.6.4.

* Tue Oct 07 2025 Antoine Tenart <atenart@redhat.com> - 1.6.3-0
- Bump to 1.6.3.

* Tue Sep 09 2025 Antoine Tenart <atenart@redhat.com> - 1.6.2-0
- Bump to 1.6.2.

* Wed Aug 27 2025 Antoine Tenart <atenart@redhat.com> - 1.6.1-0
- Bump to 1.6.1.

* Wed Aug 20 2025 Antoine Tenart <atenart@redhat.com> - 1.6.0-0
- Bump to 1.6.0.

* Fri Mar 21 2025 Antoine Tenart <atenart@redhat.com> - 1.5.2-0
- Bump to 1.5.2.
- Fix conntrack zone id being truncated.
- Fix 2 BPF verifier issues.

* Mon Jan 27 2025 Antoine Tenart <atenart@redhat.com> - 1.5.1-0
- Bump to 1.5.1.
- Fixing segfaults when using UDST probes.

* Wed Dec 18 2024 Antoine Tenart <atenart@redhat.com> - 1.5.0-0
- Bump to 1.5.0.
- Python bindings.
- Improved meta-filtering.
- ifdump profile.
- Many other improvements.

* Wed Apr 24 2024 Antoine Tenart <atenart@redhat.com> - 1.4.0-0
- Bump to 1.4.0.
- Auto-completion.
- Bitfield support in meta-filtering.
- New inspect command.
- Probe-stack mode.
- Many other improvements.

* Mon Mar 04 2024 Antoine Tenart <atenart@redhat.com> - 1.3.2-0
- Bump to 1.3.1.
- Wait for all probes to be installed before starting the collection.
- Update btf-rs to 1.1.

* Fri Jan 19 2024 Antoine Tenart <atenart@redhat.com> - 1.3.1-0
- Bump to 1.3.1.
- Improved symbols validation.
- Fixed packet size computation in BPF for some cases.
- Improved meta filtering input validation.
- Better fixed a BPF verifier issue on older kernels.
- Fixed a BPF verifier issue on newer kernels.

* Wed Dec 20 2023 Antoine Tenart <atenart@redhat.com> - 1.3.0-0
- Bump to 1.3.0.
- Pcap post-processing command.
- Meta filtering support.
- L3 filtering support.
- Wildcard support for all probe types (was kprobe-only).
- Pager support in post-processing commands.
- Non-core drop reasons support.
- Improved logging.
- Mulitple improvements & fixes.

* Fri Nov 24 2023 Antoine Tenart <atenart@redhat.com> - 1.2.1-0
- Bump to 1.2.0.
- Multiple OvS related bug fixes.

* Thu Sep 28 2023 Antoine Tenart <atenart@redhat.com> - 1.2.0-0
- Bump to 1.2.0.
- Performances improvements.
- Conntrack support.
- ARP support in the skb collector.
- New actions in the OvS collector.
- Bug fixes.

* Tue Jul 25 2023 Antoine Tenart <atenart@redhat.com> - 1.1.0-0
- Bump to 1.1.0: better CoreOS & container environments support.

* Thu Jun 15 2023 Antoine Tenart <atenart@redhat.com> - 1.0.0-0
- Initial release.
