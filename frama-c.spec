# Some ideas for this spec file taken from a prior attempt by Richard
# W. M. Jones

#  General Information
# This program has its own version of cil, there is an ocaml-cil upon which this
# based, however the version contained in this package has custom mods that
# are not availible with the ocaml-cil because the upstream has
# forked their own version of cil.

%global debug_package %{nil}
%global __strip /usr/bin/true
%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)
%if %opt
%global ocamlbest opt
%else
%global ocamlbest byte
%endif

%global pkgversion Oxygen-20120901

Name:           frama-c
Version:        1.8
Release:        2%{?dist}
Summary:        Framework for source code analysis of C software

Group:          Development/Libraries
# Licensing breakdown in source file frama-c-1.6-licensing
License:        LGPLv2 and GPLv2 and GPLv2+ and BSD and (QPL with exceptions)
URL:            http://frama-c.com/
Source0:        http://frama-c.com/download/%{name}-%{pkgversion}.tar.gz
Source1:        frama-c-1.6.licensing
Source2:        %{name}-gui.desktop
Source3:        acsl.el
# Post-release fixes from upstream
Patch0:         %{name}-fixes.patch

BuildRequires:  alt-ergo
BuildRequires:  coq
BuildRequires:  desktop-file-utils
BuildRequires:  emacs-nox xemacs-nox
BuildRequires:  graphviz
BuildRequires:  gtksourceview2-devel
BuildRequires:  libgnomecanvas-devel
BuildRequires:  ltl2ba
BuildRequires:  ocaml
BuildRequires:  ocaml-findlib-devel
BuildRequires:  ocaml-lablgtk-devel
BuildRequires:  ocaml-ocamldoc
BuildRequires:  ocaml-ocamlgraph-devel

Requires:       cpp
Requires:       graphviz
Requires:       ltl2ba

# ocaml only available on these:
ExclusiveArch:  %{ocaml_arches}

# Filter out bogus requires
%global __requires_exclude ocaml\\\((Formula|GtkSourceView2_types|Ltlast|Mcfg|Memory|Mfloat|Mint|Mlogic|Mvalues|Mwp|Promelaast)\\\)

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
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and signature files for
developing applications that use %{name}. In particular, this package
is necessary to compile plug ins for Frama-C.

%package doc
Summary:        Large documentation files for %{name}
Group:          Documentation 
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description doc
Large documentation files for %{name}.

%package emacs
Summary:        Emacs support file for ACSL markup
Group:          Development/Languages
License:        LGPLv2
Requires:       %{name} = %{version}-%{release}
Requires:       emacs(bin)
BuildArch:      noarch

%description emacs
This package contains an Emacs support file for working with C source
files marked up with ACSL.

%package emacs-el
Summary:        Emacs source file for ACSL markup
Group:          Development/Languages
License:        LGPLv2
Requires:       %{name}-emacs = %{version}-%{release}
BuildArch:      noarch

%description emacs-el
This package contains the Emacs source file for working with C source
files marked up with ACSL.  This package is not needed to use the Emacs
support.

%package xemacs
Summary:        XEmacs support file for ACSL markup
Group:          Development/Languages
License:        LGPLv2
Requires:       %{name} = %{version}-%{release}
Requires:       xemacs(bin), xemacs-packages-extra
BuildArch:      noarch

%description xemacs
This package contains an XEmacs support file for working with C source
files marked up with ACSL.

%package xemacs-el
Summary:        XEmacs source file for ACSL markup
Group:          Development/Languages
License:        LGPLv2
Requires:       %{name}-xemacs = %{version}-%{release}
BuildArch:      noarch

%description xemacs-el
This package contains the XEmacs source file for working with C source
files marked up with ACSL.  This package is not needed to use the XEmacs
support.

%prep
%setup -q -n %{name}-%pkgversion
%patch0

# Fix encodings
iconv -f iso-8859-1 -t utf8 man/frama-c.1 > man/frama-c.1.conv
touch -r man/frama-c.1 man/frama-c.1.conv
mv -f man/frama-c.1.conv man/frama-c.1

# Allow use of alt-ergo 0.94
sed -i 's/0\.92\.2/0.94/' configure
sed -i 's/0\.92\.2/0.94/' src/wp/configure

%build
# This option prints the actual make commands so we can see what's
# happening (eg: for debugging the spec file)
%global framac_make_options VERBOSEMAKE=yes OCAMLBEST=%{ocamlbest}

# Fake the existence of why so the plugin is built
touch why why-dp
chmod a+x why why-dp
PATH=${PATH}:${PWD}

%configure
make %{framac_make_options}

%install
make install DESTDIR=%{buildroot} %{framac_make_options}

%if %opt
strip %{buildroot}%{_bindir}/frama-c
strip %{buildroot}%{_bindir}/frama-c-gui
strip %{buildroot}%{_libdir}/frama-c/plugins/*.cmxs
strip %{buildroot}%{_libdir}/frama-c/plugins/gui/*.cmxs
%else
mv -f %{buildroot}%{_bindir}/frama-c.byte %{buildroot}%{_bindir}/frama-c
mv -f %{buildroot}%{_bindir}/frama-c-gui.byte %{buildroot}%{_bindir}/frama-c-gui
%endif
desktop-file-install                                    \
--dir=${RPM_BUILD_ROOT}%{_datadir}/applications/         \
%{SOURCE2}

# Install and bytecompile the XEmacs file
mkdir -p %{buildroot}%{_xemacs_sitelispdir}
cp -p share/acsl.el %{buildroot}%{_xemacs_sitelispdir}
cd %{buildroot}%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} acsl.el
mkdir -p %{buildroot}%{_xemacs_sitestartdir}
cp -p %{SOURCE3} %{buildroot}%{_xemacs_sitestartdir}

# Install and bytecompile the Emacs file
mkdir -p %{buildroot}%{_emacs_sitelispdir}
mv %{buildroot}%{_datadir}/frama-c/acsl.el %{buildroot}%{_emacs_sitelispdir}
chmod a-x %{buildroot}%{_emacs_sitelispdir}/acsl.el
cd %{buildroot}%{_emacs_sitelispdir}
%{_emacs_bytecompile} acsl.el
mkdir -p %{buildroot}%{_emacs_sitestartdir}
cp -p %{SOURCE3} %{buildroot}%{_emacs_sitestartdir}

# The install step adds lots of spurious executable bits
find %{buildroot}%{_datadir}/frama-c -type f -perm /0111 | \
xargs chmod a-x %{buildroot}%{_libdir}/frama-c/*.cmx \
                %{buildroot}%{_mandir}/man1/*

%files
%doc licenses/* doc/manuals/user-manual.pdf VERSION
%{_bindir}/*
%exclude %{_bindir}/frama-c.byte
%exclude %{_bindir}/frama-c-gui.byte
%exclude %{_bindir}/ptests.byte
%exclude %{_libdir}/frama-c/*.cmo
%exclude %{_libdir}/frama-c/*.cmx
%exclude %{_libdir}/frama-c/*.o
%{_libdir}/frama-c
%dir %{_datadir}/frama-c/
%{_datadir}/frama-c/*.gif
%{_datadir}/frama-c/*.ico
%{_datadir}/frama-c/*.png
%{_datadir}/applications/*.desktop
%{_mandir}/man1/*

%files devel
%doc doc/manuals/plugin-development-guide.pdf
%{_datadir}/frama-c/*
%{_libdir}/frama-c/*.cmo
%{_libdir}/frama-c/*.cmx
%{_libdir}/frama-c/*.o
%exclude %{_datadir}/frama-c/*.gif
%exclude %{_datadir}/frama-c/*.ico
%exclude %{_datadir}/frama-c/*.png
%exclude %{_datadir}/frama-c/manuals

%files doc
%doc doc/code/*.txt
%doc doc/manuals/acsl*
%doc doc/manuals/aorai-manual.pdf
%doc doc/manuals/metrics-manual.pdf
%doc doc/manuals/rte-manual.pdf
%doc doc/manuals/value-analysis.pdf
%doc doc/manuals/wp-manual.pdf
%doc doc/manuals/wp-tutorial.pdf

%files emacs
%{_emacs_sitelispdir}/acsl.elc
%{_emacs_sitestartdir}/acsl.el

%files emacs-el
%{_emacs_sitelispdir}/acsl.el

%files xemacs
%{_xemacs_sitelispdir}/acsl.elc
%{_xemacs_sitestartdir}/acsl.el

%files xemacs-el
%{_xemacs_sitelispdir}/acsl.el

%changelog
* Mon Oct 22 2012 Jerry James <loganjerry@gmail.com> - 1.8-2
- Update the Requires filter for Oxygen

* Fri Oct 19 2012 Jerry James <loganjerry@gmail.com> - 1.8-1
- Update to Oxygen version

* Tue Sep 11 2012 Jerry James <loganjerry@gmail.com> - 1.7-9
- Disable dangerous code in src/type/type.ml that leads to segfaults.

* Mon Aug 27 2012 Jerry James <loganjerry@gmail.com> - 1.7-8
- Use a vastly simpler patch for OCaml 4 that fixes the native build.

* Fri Aug  3 2012 Jerry James <loganjerry@gmail.com> - 1.7-7
- Shipping the bytecode version works better if it isn't stripped.

* Fri Aug  3 2012 Jerry James <loganjerry@gmail.com> - 1.7-6
- Use upstream's version of the ocamlgraph patch.
- Ship the bytecode binaries until the native breakage is diagnosed.

* Mon Jul 30 2012 Richard W.M. Jones <rjones@redhat.com> - 1.7-5
- Rebuild for OCaml 4.00.0 official.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jan  9 2012 Jerry James <loganjerry@gmail.com> - 1.7-3
- Rebuild for OCaml 3.12.1

* Tue Nov  8 2011 Jerry James <loganjerry@gmail.com> - 1.7-2
- Rebuild to eliminate libpng dependency

* Tue Oct 25 2011 Jerry James <loganjerry@gmail.com> - 1.7-1
- Update to Nitrogen version

* Mon Jul 11 2011 Jerry James <loganjerry@gmail.com> - 1.6-1
- Update to Carbon version
- Removed unnecessary spec file elements (BuildRoot, etc.)
- Update approach to filtering provides and requires
- Do not filter as much; why should Require some of the filtered names
- Add (X)Emacs support packages
- Add doc subpackage to hold large manual PDFs
- Support for gtksourceview 1.x has been dropped

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
