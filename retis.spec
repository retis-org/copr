Name:		retis
Version:	1.5.2
Release:	0%{?dist}
Summary:	Tracing packets in the Linux networking stack, using eBPF and interfacing with control and data paths such as OvS or Netfilter.
License:	GPLv2

URL:		https://github.com/retis-org/retis
Source:		https://github.com/retis-org/retis/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:		mtls-dialect.diff

%if 0%{?fedora} >= 34
BuildRequires:	rust-packaging
%else
BuildRequires:	rust-toolset
BuildRequires:	rustfmt
%endif

# Following dependencies only when not stictly using rust-packaging.
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
cat > .cargo/config << EOF
[build]
rustc = "$HOME/.cargo/bin/rustc"
rustdoc = "$HOME/.cargo/bin/rustdoc"

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

%build
%if 0%{?rhel} == 8
/usr/bin/env CARGO_HOME=.cargo CARGO_CMD_OPTS="--no-default-features" make %{?_smp_mflags} release
%else
/usr/bin/env CARGO_HOME=.cargo make %{?_smp_mflags} release
%endif

%install
%if 0%{?rhel} == 8
/usr/bin/env CARGO_HOME=.cargo CARGO_INSTALL_OPTS="--no-track --no-default-features" CARGO_CMD_OPTS="--no-default-features" make %{?_smp_mflags} install
%else
/usr/bin/env CARGO_HOME=.cargo CARGO_INSTALL_OPTS="--no-track" make %{?_smp_mflags} install
%endif
install -m 0755 -d %{buildroot}%{_sysconfdir}/retis/profiles
install -m 0644 retis/profiles/* %{buildroot}%{_sysconfdir}/retis/profiles

%check
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
%{_sysconfdir}/retis/profiles

%changelog
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
