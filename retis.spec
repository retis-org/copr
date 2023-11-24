Name:		retis
Version:	1.2.1
Release:	0%{?dist}
Summary:	Tracing packets in the Linux networking stack, using eBPF and interfacing with control and data paths such as OvS or Netfilter.
License:	GPLv2

URL:		https://github.com/retis-org/retis
Source:		https://github.com/retis-org/retis/archive/v%{version}/%{name}-%{version}.tar.gz

%if 0%{?fedora} >= 34
BuildRequires:	rust-packaging
%else
BuildRequires:	rust-toolset
BuildRequires:	rustfmt
BuildRequires:	llvm
%endif

# Following dependencies only when not stictly using rust-packaging.
%if 1
BuildRequires:	clang-devel
BuildRequires:	curl
BuildRequires:	elfutils-libelf-devel
BuildRequires:	libpcap-devel
BuildRequires:	zlib-devel
%endif

%description
Tracing packets in the Linux networking stack, using eBPF and interfacing with control and data paths such as OpenVSwitch.

%prep
%if 0%{?fedora} >= 34
%autosetup -n %{name}-%{version}
%else
%setup -q -n %{name}-%{version}
%endif
%if 0
%cargo_prep
# Following dependencies only when not stictly using rust-packaging.
%else
%{__mkdir} -p .cargo
cat > .cargo/config << EOF
[build]
rustc = "$HOME/.cargo/bin/rustc"
rustdoc = "$HOME/.cargo/bin/rustdoc"

%if 0%{?fedora}
[profile.rpm]
inherits = "release"
opt-level = %{rustflags_opt_level}
codegen-units = %{rustflags_codegen_units}
debug = %{rustflags_debuginfo}
strip = "none"
%else
[profile.rpm]
inherits = "release"
opt-level = "%{rustflags_opt_level}"
codegen-units = "%{rustflags_codegen_units}"
debug = "%{rustflags_debuginfo}"
strip = "none"
%endif

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
%endif

%build
%cargo_build

%install
%cargo_install
install -m 0755 -d %{buildroot}%{_sysconfdir}/retis/profiles
install -m 0644 profiles/* %{buildroot}%{_sysconfdir}/retis/profiles

%check
%cargo_test

%files
%license LICENSE
%doc README.md
%{_bindir}/retis
%{_sysconfdir}/retis/profiles

%changelog
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
