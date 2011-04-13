# Some ideas for this spec file taken from a prior attempt by Richard
# W. M. Jones

#  General Information
# This program has its own version of cil, there is an ocaml-cil upon which this
# based, however the version contained in this package has custom mods that
# are not availible with the ocaml-cil because the upstream has
# forked their own version of cil.


%global debug_package %{nil}
%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)
%if %opt
%global ocamlbest opt
%else
%global ocamlbest byte
%endif

%global pkgversion Boron-20100401

Name:           frama-c
Version:        1.5
Release:        3.1%{?dist}
Summary:        Framework for source code analysis of C software

Group:          Development/Libraries
# Licensing breakdown in source file frama-c-1.4-licensing
License:        LGPLv2 and GPLv2 and GPLv2+ and BSD and (QPL with modifications)
URL:            http://frama-c.cea.fr/
Source0:        http://frama-c.cea.fr/download/%{name}-%{pkgversion}.tar.gz
Source1:        frama-c-1.5.licensing
Source2:        %{name}-gui.desktop


BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires: ocaml >= 3.11.0, ocaml-findlib-devel, ocaml-lablgtk-devel >= 2.14.0-5 , ocaml-ocamlgraph-devel
BuildRequires: gtksourceview >= 1.0.0, gtksourceview-devel, gtksourceview2, gtksourceview2-devel
BuildRequires: libgnomecanvas-devel
BuildRequires: desktop-file-utils
BuildRequires: ltl2ba >= 1.1

# specialized dependency generator used because of issues with OCAML at the 
# suggestion of the OCAML group

%define _use_internal_dependency_generator 0
%define __find_requires /usr/lib/rpm/ocaml-find-requires.sh  -i GtkSourceView2_types -i Ltlast -i Promelaast -i Cil_types -i Db_types -i Dgraph -i Lattice_With_Isotropy -i Logic_ptree -i Signature
%define __find_provides /usr/lib/rpm/ocaml-find-provides.sh -i GtkSourceView2_types -i Ltlast -i Promelaast -i Cil_types -i Db_types -i Dgraph -i Lattice_With_Isotropy -i Logic_ptree -i Signature


Requires: graphviz >= 2.0.0
Requires: gtksourceview >= 1.0.0
Requires: ocaml >= 3.11.0

# ocaml only available on these:
ExclusiveArch: alpha armv4l %{ix86} ia64 x86_64 ppc ppc64 sparc sparcv9 ppc64


%description
Frama-C is a suite of tools dedicated to the analysis of the source
code of software written in C.

Frama-C gathers several static analysis techniques in a single
collaborative framework. The collaborative approach of Frama-C allows
static analyzers to build upon the results already computed by other
analyzers in the framework. Thanks to this approach, Frama-C provides
sophisticated tools, such as a slicer and dependency analysis.

%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and signature files for
developing applications that use %{name}. In particular, this package
is necessary to compile plug ins for Frama-C.

%prep
%setup -q -n %{name}-%pkgversion


iconv -f iso-8859-1 -t utf8 man/frama-c.1 > man/frama-c.1.conv && mv man/frama-c.1.conv man/frama-c.1

%build

# This option prints the actual make commands so we can see what's
# happening (eg: for debugging the spec file)
%global framac_make_options VERBOSEMAKE=yes OCAMLBEST=%{ocamlbest}

# Must disable plug-ins that no longer work, else running will cause warnings.
%configure --disable-security_slicing --disable-aorai
make %{framac_make_options}


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} %{framac_make_options}
strip %{buildroot}/%{_bindir}/frama-c
strip %{buildroot}/%{_bindir}/frama-c-gui
chmod -x  %{buildroot}/usr/share/frama-c/libc/*.h
chmod -x  %{buildroot}/usr/share/frama-c/libc/*.c
chmod -x  %{buildroot}/usr/share/frama-c/libc/sys/*.h
chmod -x  %{buildroot}/usr/share/frama-c/libc/netinet/*.h
desktop-file-install                                    \
--dir=${RPM_BUILD_ROOT}%{_datadir}/applications/         \
%{SOURCE2}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/*
%doc licenses/LGPLv2.1
%doc licenses/LGPLv3
%doc licenses/Q_MODIFIED_LICENSE
%doc cil/LICENSE

%exclude %{_bindir}/frama-c.byte
%exclude %{_bindir}/frama-c-gui.byte
%exclude %{_bindir}/ptests.byte
%exclude %{_libdir}/frama-c/*.cmo
%exclude %{_libdir}/frama-c/*.cmx
%exclude %{_libdir}/frama-c/*.o
%{_libdir}/frama-c
%dir %{_datadir}/frama-c/
%{_datadir}/frama-c/*
%{_datadir}/applications/*.desktop
%{_mandir}/man1/*
%exclude %{_datadir}/frama-c

%files devel
%defattr(-,root,root,-)
%{_datadir}/frama-c/*
%{_libdir}/frama-c/*.cmo
%{_libdir}/frama-c/*.cmx
%{_libdir}/frama-c/*.o
%{_mandir}/man1/*
%exclude %{_datadir}/frama-c/why
%exclude %{_datadir}/frama-c/manuals
%exclude %{_mandir}/man1/frama-c.1.gz
%exclude %{_mandir}/man1/frama-c-gui.1.gz

%post 


%changelog
* Wed Apr 13 2011 Karsten Hopp <karsten@redhat.com> 1.5-3.1
- add ppc64 to archs with ocaml

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jan 22 2011 Dan Horák <dan[at]danny.cz> - 1.5-2
- updated the supported arch list

* Sat Jul 07 2010 Mark Rader <msrader@gmail.com> 1.5-1
- Upgraded Frama C to Boron version and added ltl2ba dependencies.

* Mon Jul 05 2010 Mark Rader <msrader@gmail.com> 1.4-4
- Modified spec file to add new OCAML dependency structure for FC-13

* Sun Jun 06 2010 Mark Rader <msrader@gmail.com> 1.4-3
- Added documentation to explain the various licensing entries.
- Added .desktop file

* Wed May 24 2010 Mark Rader <msrader@gmail.com> 1.4-2
- Add SELinux context settings.

* Wed Feb 10 2010 Alan Dunn <amdunn@gmail.com> 1.4-1

- Initial Fedora RPM

