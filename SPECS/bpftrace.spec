Name:           bpftrace
Version:        0.16.0
Release:        2%{?dist}
Summary:        High-level tracing language for Linux eBPF
License:        ASL 2.0

%define cereal_version 1.3.2

URL:            https://github.com/iovisor/bpftrace
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# Cereal is a header-only serialization library which is not packaged into
# RHEL9, so we download it manually. This is ok to do as it is only necessary
# for build.
Source1:        https://github.com/USCiLab/cereal/archive/v%{cereal_version}/cereal-%{cereal_version}.tar.gz

Patch0:         %{name}-%{version}-IR-builder-get-rid-of-getPointerElementType-calls.patch
Patch1:         %{name}-%{version}-tcpdrop-Fix-ERROR-Error-attaching-probe-kprobe-tcp_d.patch

Patch10:        %{name}-%{version}-RHEL-aarch64-fixes-statsnoop-and-opensnoop.patch

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
BuildRequires:  bcc-devel >= 0.19.0-8
BuildRequires:  libbpf-devel
BuildRequires:  libbpf-static
BuildRequires:  binutils-devel


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
%cmake_build


%install
# The post hooks strip the binary which removes
# the BEGIN_trigger and END_trigger functions
# which are needed for the BEGIN and END probes
%global __os_install_post %{nil}
%global _find_debuginfo_opts -g

%cmake_install

# Fix shebangs (https://fedoraproject.org/wiki/Packaging:Guidelines#Shebang_lines)
find %{buildroot}%{_datadir}/%{name}/tools -type f -exec \
  sed -i -e '1s=^#!/usr/bin/env %{name}\([0-9.]\+\)\?$=#!%{_bindir}/%{name}=' {} \;


%files
%doc README.md CONTRIBUTING-TOOLS.md
%doc docs/reference_guide.md docs/tutorial_one_liners.md
%license LICENSE
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/tools
%dir %{_datadir}/%{name}/tools/doc
%{_bindir}/%{name}
%{_bindir}/%{name}-aotrt
%{_mandir}/man8/*
%attr(0755,-,-) %{_datadir}/%{name}/tools/*.bt
%{_datadir}/%{name}/tools/doc/*.txt
# Do not include old versions of tools, they do not work on RHEL 9
%exclude %{_datadir}/%{name}/tools/old

%changelog
* Tue Jan 03 2023 Viktor Malik <vmalik@redhat.com> - 0.16.0-2
- Fix missing kprobe attachpoints for bio* tools (s390x, ppc64le)
- Rebuild for libbpf 1.0.0
- Resolves: rhbz#2157829
- Related: rhbz#2157592

* Fri Dec 16 2022 Viktor Malik <vmalik@redhat.com> - 0.16.0-1
- Rebase on bpftrace 0.16.0 (rhbz#2121920)
- Rebuild for LLVM 15 (rhbz#2118995)
- Download the cereal library (not packaged into RHEL9)
- Fixed several tools (rhbz#1975148, rhbz#2088577, rhbz#2128208, rhbz#2073675,
  rhbz#2073770)
- Resolve conflicts between bpftrace and bcc manpages (rhbz#2075076)

* Mon May 16 2022 Jerome Marchand <jmarchan@redhat.com> - 0.13.1-1
- Rebase to bpftrace 0.13.1
- Rebuild for LLVM14

* Mon Feb 21 2022 Viktor Malik <vmalik@redhat.com> - 0.12.1-8
- Fix wildcard listing bug
- Fix bio* tools

* Thu Dec 02 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1.7
- Bump up required bcc version.

* Thu Dec 02 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1.6
- Rebuild on LLVM13

* Mon Oct 18 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1.5
- threadsnoop: probe libpthread.so.0
- Fix aarch64 failures

* Mon Oct 18 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1.4
- Fix gating

* Fri Oct 15 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.1-3
- Fix mdflush (rhbz#1967567)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 0.12.1-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu May 27 2021 Jerome Marchand <jmarchan@redhat.com> - 0.12.0-1
- Rebase to bpftrace 0.12.1

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 0.11.0-10
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb 12 2021 Jerome Marchand <jmarchan@redhat.com> - 0.11.0-9
- Last build failed: rebuild.

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Tom Stellard <tstellar@redhat.com> - 0.11.0-7
- Rebuild for clang-11.1.0

* Fri Dec 04 2020 Jeff Law <law@redhat.com> - 0.11.0-6
- Fix missing #include for gcc-11

* Fri Nov 13 2020 Jerome Marchand <jmarchan@redhat.com> - 0.11.0-5
- Rebuilt for LLVM 11

* Tue Aug 04 2020 Augusto Caringi <acaringi@redhat.com> - 0.11.0-4
- Fix FTBFS due to cmake wide changes #1863295
- Fix 'bpftrace symbols are stripped' #1865787

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Jul 16 2020 Augusto Caringi <acaringi@redhat.com> - 0.11.0-1
* Rebased to version 0.11.0

* Tue May 19 2020 Augusto Caringi <acaringi@redhat.com> - 0.10.0-2
- Rebuilt for new bcc/libbpf versions

* Tue Apr 14 2020 Augusto Caringi <acaringi@redhat.com> - 0.10.0-1
- Rebased to version 0.10.0
- Dropped support for s390x temporaly due to build error

* Thu Feb 06 2020 Augusto Caringi <acaringi@redhat.com> - 0.9.4-1
- Rebased to version 0.9.4

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Nov 21 2019 Augusto Caringi <acaringi@redhat.com> - 0.9.3-1
- Rebased to version 0.9.3

* Thu Aug 01 2019 Augusto Caringi <acaringi@redhat.com> - 0.9.2-1
- Rebased to version 0.9.2

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 26 2019 Augusto Caringi <acaringi@redhat.com> - 0.9.1-1
- Rebased to version 0.9.1

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
