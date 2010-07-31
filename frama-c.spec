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

%global pkgversion Beryllium-20090902

Name:           frama-c
Version:        1.4
Release:        6%{?dist}
Summary:        Framework for source code analysis of C software

Group:          Development/Libraries
# Licensing breakdown in source file frama-c-1.4-licensing
License:        LGPLv2 and GPLv2 and GPLv2+ and BSD and (QPL with modifications)
URL:            http://frama-c.cea.fr/
Source0:        http://frama-c.cea.fr/download/%{name}-%{pkgversion}.tar.gz
Source1:        frama-c-1.4-licensing
Source2:        %{name}.desktop

#Patch to use new extensions in fedora 13.  This patch changes the configuration to 
#look for a different file extension in ocaml
Patch0:         frama-c-1.4-fix-ocamlgraph-detection.patch

# There are four patches from Medhi Dogguy in the Debian package:
#
# 0001-Fix-weak-pattern-matching-in-dynlink_lower_311_byte..patch
#
# This seems to apply for us as well, keeping Debian filename

Patch1:         frama-c-Fix-weak-pattern-matching-in-dynlink_lower_311_byte.patch

#Patch to use new extensions in fedora 13.  This patch changes the configuration to 
#look for a different file extension in ocaml
 
Patch2:         frama-c-1.4-ptests-fix-for-ocaml-3.11.2.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires: ocaml >= 3.11.0, ocaml-findlib-devel, ocaml-lablgtk-devel, ocaml-ocamlgraph-devel
BuildRequires: gtksourceview >= 1.0.0, gtksourceview-devel
BuildRequires: libgnomecanvas-devel
BuildRequires: desktop-file-utils

# specialized dependency generator used because of issues with OCAML at the 
# suggestion of the OCAML group

%define _use_internal_dependency_generator 0
%define __find_requires /usr/lib/rpm/ocaml-find-requires.sh  -i GtkSourceView_types -i Ltlast -i Promelaast
%define __find_provides /usr/lib/rpm/ocaml-find-provides.sh -i GtkSourceView_types -i Ltlast -i Promelaast


Requires: graphviz >= 2.0.0
Requires: gtksourceview >= 1.0.0
Requires: ocaml >= 3.11.0


ExcludeArch: PPC, PPC64, ARM, IA64, MIPS, S390


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

%patch0 -p1
%patch1 -p1

%if 0%{?fedora} >= 13
%patch2 -p1
%endif

iconv -f iso-8859-1 -t utf8 man/frama-c.1 > man/frama-c.1.conv && mv man/frama-c.1.conv man/frama-c.1

%build

# This option prints the actual make commands so we can see what's
# happening (eg: for debugging the spec file)
%global framac_make_options VERBOSEMAKE=yes OCAMLBEST=%{ocamlbest}

%configure
make %{framac_make_options}


%install
rm -rf %{buildroot}

make install DESTDIR=%{buildroot} %{framac_make_options}
strip %{buildroot}/%{_bindir}/frama-c
strip %{buildroot}/%{_bindir}/frama-c-gui
strip %{buildroot}/%{_libdir}/frama-c/plugins/Ltl_to_acsl.cmxs

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
%dir %{_datadir}/frama-c
%{_datadir}/frama-c/frama-c.rc
%{_datadir}/frama-c/why
%{_datadir}/frama-c/manuals
%{_datadir}/applications/*.desktop
%{_mandir}/man1/*
%exclude %{_datadir}/frama-c

%files devel
%defattr(-,root,root,-)
%{_datadir}/frama-c/*
%{_mandir}/man1/*
%exclude %{_datadir}/frama-c/why
%exclude %{_datadir}/frama-c/manuals
%exclude %{_mandir}/man1/frama-c.1.gz
%exclude %{_mandir}/man1/frama-c-gui.1.gz

%post 
semanage fcontext -a -t textrel_shlib_t '%{_libdir}/frama-c/plugins/Ltl_to_acsl.cmxs'
restorecon -v '%{_libdir}/frama-c/plugins/Ltl_to_acsl.cmxs'

%changelog
* Sat Jul 31 2010 Mark Rader <msrader@gmail.com> 1.4-6
- Modified the gui file and directory to correct potential ownership problem.

* Sun Jul 18 2010 Mark Rader <msrader@gmail.com> 1.4-5
- Modified comments to patch 1 in spec file
- Corrected SELinux context settings

* Mon Jul 05 2010 Mark Rader <msrader@gmail.com> 1.4-4
- Modified spec file to add new OCAML dependency structure for FC-13

* Sun Jun 06 2010 Mark Rader <msrader@gmail.com> 1.4-3
- Added documentation to explain the various licensing entries.
- Added .desktop file

* Wed May 24 2010 Mark Rader <msrader@gmail.com> 1.4-2
- Add SELinux context settings.

* Wed Feb 10 2010 Alan Dunn <amdunn@gmail.com> 1.4-1

- Initial Fedora RPM

