%bcond_without llvm_static

Name:           bpftrace
Version:        0.16.0
Release:        1%{?dist}
Summary:        High-level tracing language for Linux eBPF
License:        ASL 2.0

%define cereal_version 1.3.2

URL:            https://github.com/iovisor/bpftrace
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# Cereal is a header-only serialization library which is not packaged into
# RHEL8, so we download it manually. This is ok to do as it is only necessary
# for build.
Source1:        https://github.com/USCiLab/cereal/archive/v%{cereal_version}/cereal-%{cereal_version}.tar.gz

Patch0:         %{name}-%{version}-IR-builder-get-rid-of-getPointerElementType-calls.patch
Patch1:         %{name}-%{version}-tools-old-mdflush.bt-fix-BPFTRACE_HAVE_BTF-macro.patch
Patch2:         %{name}-%{version}-tcpdrop-Fix-ERROR-Error-attaching-probe-kprobe-tcp_d.patch
Patch3:         %{name}-%{version}-RHEL8-remove-not-existing-attachpoints-from-tools.patch
Patch10:        %{name}-%{version}-RHEL-8-aarch64-fixes-statsnoop-and-opensnoop.patch

# Arches will be included as upstream support is added and dependencies are
# satisfied in the respective arches
ExclusiveArch:  x86_64 %{power64} aarch64 s390x

BuildRequires:  gcc-c++
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  cmake
BuildRequires:  elfutils-libelf-devel
BuildRequires:  zlib-devel
BuildRequires:  llvm-devel
BuildRequires:  clang-devel
BuildRequires:  bcc-devel
BuildRequires:  libbpf-devel
BuildRequires:  libbpf-static
BuildRequires:  binutils-devel

%if %{with llvm_static}
BuildRequires:  llvm-static
%endif

# We don't need kernel-devel to use bpftrace, but some tools need it
Recommends:     kernel-devel

%description
BPFtrace is a high-level tracing language for Linux enhanced Berkeley Packet
Filter (eBPF) available in recent Linux kernels (4.x). BPFtrace uses LLVM as a
backend to compile scripts to BPF-bytecode and makes use of BCC for
interacting with the Linux BPF system, as well as existing Linux tracing
capabilities: kernel dynamic tracing (kprobes), user-level dynamic tracing
(uprobes), and tracepoints. The BPFtrace language is inspired by awk and C,
and predecessor tracers such as DTrace and SystemTap


%prep
%autosetup -N -a 1
%autopatch -p1 -M 9

%ifarch aarch64
%patch10 -p1
%endif

%build
# Set CPATH so that CMake finds the cereal headers
CPATH=$PWD/cereal-%{cereal_version}/include:$CPATH
export CPATH
%cmake . \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DBUILD_TESTING:BOOL=OFF \
        -DBUILD_SHARED_LIBS:BOOL=OFF
%make_build


%install
# The post hooks strip the binary which removes
# the BEGIN_trigger and END_trigger functions
# which are needed for the BEGIN and END probes
%global __os_install_post %{nil}
%global _find_debuginfo_opts -g

%make_install

# Fix shebangs (https://fedoraproject.org/wiki/Packaging:Guidelines#Shebang_lines)
find %{buildroot}%{_datadir}/%{name}/tools -type f -exec \
  sed -i -e '1s=^#!/usr/bin/env %{name}\([0-9.]\+\)\?$=#!%{_bindir}/%{name}=' {} \;

# Some tools require old versions for RHEL8
cp %{buildroot}/%{_datadir}/%{name}/tools/old/biosnoop.bt %{buildroot}/%{_datadir}/%{name}/tools
cp %{buildroot}/%{_datadir}/%{name}/tools/old/mdflush.bt %{buildroot}/%{_datadir}/%{name}/tools


%files
%doc README.md CONTRIBUTING-TOOLS.md
%doc docs/reference_guide.md docs/tutorial_one_liners.md
%license LICENSE
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/tools
%dir %{_datadir}/%{name}/tools/doc
%dir %{_datadir}/%{name}/tools/old
%{_bindir}/%{name}
%{_bindir}/%{name}-aotrt
%{_mandir}/man8/*
%attr(0755,-,-) %{_datadir}/%{name}/tools/*.bt
%{_datadir}/%{name}/tools/doc/*.txt
# Do not include old versions of tools.
# Those that are needed were already installed as normal tools.
%exclude %{_datadir}/%{name}/tools/old

%changelog
* Wed Nov 30 2022 Viktor Malik <vmalik@redhat.com> - 0.16.0-1
- Rebase on bpftrace 0.16.0
- Rebuild for LLVM15
- Download the cereal library (not packaged into RHEL8)

* Thu Jun 02 2022 Jerome Marchand <jmarchan@redhat.com> - 0.13.1-1
- Rebase on bpftrace 0.13.1
- Rebuild on LLVM14

* Thu Dec 02 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1-4
- Rebuild on LLVM13
- Small spec cleanup

* Thu Jun 24 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1-3
- Have threadsnoop points to libpthread.so.0

* Wed Jun 09 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1-2
- Rebuild on LLVM12

* Fri Apr 30 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1-1
- Rebase on bpftrace 0.12.1

* Thu Jan 28 2021 Jerome Marchand <jmarchan@redhat.com> - 0.11.1-3
- Add missing libbpf and binutils-dev dependencies

* Wed Nov 11 2020 Jerome Marchand <jmarchan@redhat.com> - 0.11.1-2
- Fix statsnoop and opensnoop on aarch64 again

* Fri Nov 06 2020 Jerome Marchand <jmarchan@redhat.com> - 0.11.1-1
- Rebase on bpftrace 0.11.1

* Tue Oct 27 2020 Jerome Marchand <jmarchan@redhat.com> - 0.10.0-5
- Rebuild for bcc 0.16.0

* Thu Jun 11 2020 Jerome Marchand <jmarchan@redhat.com> - 0.10.0-4
- Fix KBUILD_MODNAME

* Thu Jun 11 2020 Jerome Marchand <jmarchan@redhat.com> - 0.10.0-3
- Fix ENOMEM issue on arm64 machine with many cpus
- Fix statsnoop and opensnoop on aarch64
- Drop tcpdrop on ppc64

* Tue May 05 2020 Jerome Marchand <jmarchan@redhat.com> - 0.10.0-2
- Fix libpthread path in threadsnoop

* Wed Apr 22 2020 Jerome Marchand <jmarchan@redhat.com> - 0.10.0-1
- Rebase on bpftrace 0.10.0

* Fri Nov 08 2019 Jerome Marchand <jmarchan@redhat.com> - 0.9.2-1
- Rebase on bpftrace 0.9.2

* Tue Jun 18 2019 Jerome Marchand <jmarchan@redhat.com> - 0.9-3
- Don't allow to raw_spin_lock* kprobes that can deadlock the kernel.

* Wed Jun 12 2019 Jerome Marchand <jmarchan@redhat.com> - 0.9-2
- Fixes gethostlatency
- Fixes a struct definition issue that made several tools fail
- Add CI gating

* Wed May 15 2019 Jerome Marchand <jmarchan@redhat.com> - 0.9.1
- Original build on RHEL 8

* Thu Apr 25 2019 Augusto Caringi <acaringi@redhat.com> - 0.9-3
- Rebuilt for bcc 0.9.0

* Mon Apr 22 2019 Neal Gompa <ngompa@datto.com> - 0.9-2
- Fix Source0 reference
- Use make_build macro for calling make

* Mon Apr  1 2019 Peter Robinson <pbrobinson@fedoraproject.org> 0.9-1
- Build on aarch64 and s390x

* Mon Mar 25 2019 Augusto Caringi <acaringi@redhat.com> - 0.9-0
- Updated to version 0.9

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.0-2.20181210gitc49b333
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 10 2018 Augusto Caringi <acaringi@redhat.com> - 0.0-1.20181210gitc49b333
- Updated to latest upstream (c49b333c034a6d29a7ce90f565e27da1061af971)

* Wed Nov 07 2018 Augusto Caringi <acaringi@redhat.com> - 0.0-1.20181107git029717b
- Initial import
