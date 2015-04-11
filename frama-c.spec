# Some ideas for this spec file taken from a prior attempt by Richard
# W. M. Jones

#  General Information
# This program has its own version of cil, there is an ocaml-cil upon which this
# based, however the version contained in this package has custom mods that
# are not availible with the ocaml-cil because the upstream has
# forked their own version of cil.

%global opt %(test -x %{_bindir}/ocamlopt && echo 1 || echo 0)
%if ! %opt
%global debug_package %{nil}
%endif

%global pkgversion Sodium-20150201

Name:           frama-c
Version:        1.11
Release:        2%{?dist}
Summary:        Framework for source code analysis of C software

# Licensing breakdown in source file frama-c-1.6-licensing
License:        LGPLv2 and GPLv2 and GPLv2+ and BSD and (QPL with exceptions)
URL:            http://frama-c.com/
Source0:        http://frama-c.com/download/%{name}-%{pkgversion}.tar.gz
Source1:        http://frama-c.com/download/%{name}-%{pkgversion}_api.tar.gz
Source2:        frama-c-1.6.licensing
Source3:        %{name}-gui.desktop
Source4:        %{name}-gui.appdata.xml
Source5:        acsl.el
Source6:        http://frama-c.com/download/user-manual-%{pkgversion}.pdf
Source7:        http://frama-c.com/download/plugin-development-guide-%{pkgversion}.pdf
Source8:        http://frama-c.com/download/acsl-implementation-%{pkgversion}.pdf
Source9:        http://frama-c.com/download/aorai-manual-%{pkgversion}.pdf
Source10:       http://frama-c.com/download/metrics-manual-%{pkgversion}.pdf
Source11:       http://frama-c.com/download/rte-manual-%{pkgversion}.pdf
Source12:       http://frama-c.com/download/value-analysis-%{pkgversion}.pdf
Source13:       http://frama-c.com/download/wp-manual-%{pkgversion}.pdf
# Icons created with gimp from the official upstream icon
Source14:       %{name}-icons.tar.xz
# Add back a Neon function removed in Sodium that why still needs
Patch0:         %{name}-why.patch

BuildRequires:  alt-ergo
BuildRequires:  coq
BuildRequires:  desktop-file-utils
BuildRequires:  emacs xemacs-nox
BuildRequires:  graphviz
BuildRequires:  gtksourceview2-devel
BuildRequires:  libgnomecanvas-devel
BuildRequires:  ltl2ba
BuildRequires:  ocaml
BuildRequires:  ocaml-findlib
BuildRequires:  ocaml-lablgtk-devel
BuildRequires:  ocaml-ocamldoc
BuildRequires:  ocaml-ocamlgraph-devel
BuildRequires:  ocaml-zarith-devel
BuildRequires:  why3

Requires:       cpp
Requires:       graphviz
Requires:       hicolor-icon-theme
Requires:       ltl2ba

# Filter out bogus requires
%global __requires_exclude ocaml\\\((CfgTypes|GtkSourceView2_types|Ltlast|Marks|Mcfg|Memory|Promelaast)\\\)

%description
Frama-C is a suite of tools dedicated to the analysis of the source
code of software written in C.

Frama-C gathers several static analysis techniques in a single
collaborative framework. The collaborative approach of Frama-C allows
static analyzers to build upon the results already computed by other
analyzers in the framework. Thanks to this approach, Frama-C provides
sophisticated tools, such as a slicer and dependency analysis.

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
%setup -q -n %{name}-%{pkgversion}
%setup -q -T -D -a 1 -n %{name}-%{pkgversion}
%setup -q -T -D -a 14 -n %{name}-%{pkgversion}
%patch0

# Copy in the manuals
mkdir doc/manuals
cp -p %{SOURCE6} %{SOURCE7} %{SOURCE8} %{SOURCE9} %{SOURCE10} %{SOURCE11} \
   %{SOURCE12} %{SOURCE13} doc/manuals

# Do not use the bundled version of ocamlgraph
rm -f ocamlgraph.tar.gz

# Enable debuginfo
sed -i 's/ -pack/ -g&/;s/^OPT.*=/& -g/' src/wp/qed/src/Makefile

# Link with the Fedora LDFLAGS
for flag in $RPM_LD_FLAGS; do
  sed -i "/OLINKFLAGS/s|-linkall|& -ccopt $flag|" Makefile
done

# Preserve timestamps when installing
sed -ri 's/^CP[[:blank:]]+=.*/& -p/' share/Makefile.common

# Remove spurious executable bits
find -O3 . -perm /0111 \( -name \*.ml -o -name \*.mli \) | xargs chmod 0644

# Build buckx with the right flags
sed -i "s|-O3 -Wall|%{optflags} -fPIC|" Makefile

%build
# This option prints the actual make commands so we can see what's
# happening (eg: for debugging the spec file)
%configure --enable-verbosemake
make

%install
# Prevent rebuilds containing the buildroot when installing
sed -i.orig 's/^headers::/headers:/' Makefile
touch -r Makefile.orig Makefile
sed -i.orig '/^headers::/,/^$/d' src/aorai/Makefile
touch -r src/aorai/Makefile.orig src/aorai/Makefile

make install DESTDIR=%{buildroot}

%if %opt
mv -f %{buildroot}%{_bindir}/ptests.opt %{buildroot}%{_bindir}/ptests
%else
mv -f %{buildroot}%{_bindir}/frama-c.byte %{buildroot}%{_bindir}/frama-c
mv -f %{buildroot}%{_bindir}/frama-c-gui.byte %{buildroot}%{_bindir}/frama-c-gui
mv -f %{buildroot}%{_bindir}/ptests.byte %{buildroot}%{_bindir}/ptests
%endif

# Install the desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications/ %{SOURCE3}

# Install the AppData file
mkdir -p %{buildroot}%{_datadir}/appdata
install -pm 644 %{SOURCE4} %{buildroot}%{_datadir}/appdata

# Install the icons
mkdir -p %{buildroot}%{_datadir}/icons
cp -a icons %{buildroot}%{_datadir}/icons/hicolor

# Install and bytecompile the XEmacs file
mkdir -p %{buildroot}%{_xemacs_sitelispdir}
cp -p share/acsl.el %{buildroot}%{_xemacs_sitelispdir}
pushd %{buildroot}%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} acsl.el
mkdir -p %{buildroot}%{_xemacs_sitestartdir}
cp -p %{SOURCE5} %{buildroot}%{_xemacs_sitestartdir}

# Install and bytecompile the Emacs file
mkdir -p %{buildroot}%{_emacs_sitelispdir}
mv %{buildroot}%{_datadir}/frama-c/acsl.el %{buildroot}%{_emacs_sitelispdir}
chmod a-x %{buildroot}%{_emacs_sitelispdir}/acsl.el
cd %{buildroot}%{_emacs_sitelispdir}
%{_emacs_bytecompile} acsl.el
mkdir -p %{buildroot}%{_emacs_sitestartdir}
cp -p %{SOURCE5} %{buildroot}%{_emacs_sitestartdir}
popd

# Remove files we don't actually want
rm -f %{buildroot}%{_libdir}/frama-c/*.{cmo,cmx,o}

# The install step adds lots of spurious executable bits
find %{buildroot}%{_datadir}/frama-c -type f -perm /0111 | \
xargs chmod a-x %{buildroot}%{_mandir}/man1/*

# Remove spurious executable bits on generated files
chmod 0644 src/lib/dynlink_common_interface.ml src/lib/integer.ml

%post
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%postun
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc VERSION
%license licenses/*
%{_bindir}/*
%if %opt
%exclude %{_bindir}/frama-c.byte
%exclude %{_bindir}/frama-c-gui.byte
%exclude %{_bindir}/ptests.byte
%endif
%{_libdir}/frama-c/
%{_datadir}/frama-c/
%{_datadir}/appdata/%{name}-gui.appdata.xml
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_mandir}/man1/*

%files doc
%doc doc/code/*.{css,htm,txt}
%doc doc/manuals/acsl-implementation-%{pkgversion}.pdf
%doc doc/manuals/aorai-manual-%{pkgversion}.pdf
%doc doc/manuals/metrics-manual-%{pkgversion}.pdf
%doc doc/manuals/plugin-development-guide-%{pkgversion}.pdf
%doc doc/manuals/rte-manual-%{pkgversion}.pdf
%doc doc/manuals/user-manual-%{pkgversion}.pdf
%doc doc/manuals/value-analysis-%{pkgversion}.pdf
%doc doc/manuals/wp-manual-%{pkgversion}.pdf
%doc frama-c-api

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
* Sat Apr 11 2015 Jerry James <loganjerry@gmail.com> - 1.11-2
- Rebuild for coq 8.4pl6

* Wed Mar 18 2015 Jerry James <loganjerry@gmail.com> - 1.11-1
- Update to Sodium version
- Drop all patches; all have been upstreamed
- Add -why patch to fix the why build

* Wed Feb 18 2015 Richard W.M. Jones <rjones@redhat.com> - 1.10-21
- ocaml-4.02.1 rebuild.

* Thu Oct 30 2014 Jerry James <loganjerry@gmail.com> - 1.10-20
- Rebuild for coq 8.4pl5

* Tue Oct 14 2014 Jerry James <loganjerry@gmail.com> - 1.10-19
- Rebuild for ocaml-zarith 1.3

* Thu Sep 18 2014 Jerry James <loganjerry@gmail.com> - 1.10-18
- Bump release and rebuild

* Thu Sep 18 2014 Jerry James <loganjerry@gmail.com> - 1.10-17
- Rebuild for why3 0.85

* Thu Sep  4 2014 Jerry James <loganjerry@gmail.com> - 1.10-16
- Adapt to why3 0.84

* Tue Sep  2 2014 Jerry James <loganjerry@gmail.com> - 1.10-15
- Rebuild for final ocaml 4.02.0 release
- Fix license handling

* Mon Aug 25 2014 Jerry James <loganjerry@gmail.com> - 1.10-14
- ocaml-4.02.0+rc1 rebuild.

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Aug 09 2014 Richard W.M. Jones <rjones@redhat.com> - 1.10-12
- ocaml-4.02.0-0.8.git10e45753.fc22 rebuild.

* Mon Aug  4 2014 Jerry James <loganjerry@gmail.com> - 1.10-11
- BR emacs instead of emacs-nox, which has gone away

* Fri Aug 01 2014 Richard W.M. Jones <rjones@redhat.com> - 1.10-11
- Bump release and rebuild.

* Fri Aug 01 2014 Richard W.M. Jones <rjones@redhat.com> - 1.10-10
- Bump release and rebuild.

* Fri Jul 25 2014 Richard W.M. Jones <rjones@redhat.com> - 1.10-9
- Rebuild for OCaml 4.02.0 beta.

* Mon Jul 21 2014 Jerry James <loganjerry@gmail.com> - 1.10-8
- Add comment to desktop file

* Thu Jun 26 2014 Jerry James <loganjerry@gmail.com> - 1.10-7
- Set LDFLAGS in a less destructive way (bz 1105265)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 13 2014 Jerry James <loganjerry@gmail.com> - 1.10-5
- Rebuild for coq 8.4pl4

* Mon Apr 21 2014 Jerry James <loganjerry@gmail.com> - 1.10-4
- Rebuild for ocamlgraph 1.8.5; add -ocamlgraph patch to adapt

* Tue Apr 15 2014 Richard W.M. Jones <rjones@redhat.com> - 1.10-3
- Remove ocaml_arches macro (RHBZ#1087794).

* Mon Mar 24 2014 Jerry James <loganjerry@gmail.com> - 1.10-2
- Fix the icon name in the desktop file
- Install icons
- Drop unnecessary gmp-devel BR (pulled in by ocaml-zarith-devel)
- Fix permissions later, else they get reset to the bad values

* Mon Mar 17 2014 Jerry James <loganjerry@gmail.com> - 1.10-1
- Update to Neon version
- All patches have been upstreamed; drop them
- The manuals are no longer included in the source distribution; add as Sources
- BR ocaml-findlib instead of ocaml-findlib-devel
- BR why3 to get coq + why3 support in the wp plugin

* Wed Feb 26 2014 Jerry James <loganjerry@gmail.com> - 1.9-9
- Rebuild for ocaml-ocamlgraph 1.8.4; add -ocamlgraph patch to adapt.
- Add an Appdata file.

* Wed Oct 02 2013 Richard W.M. Jones <rjones@redhat.com> - 1.9-8
- Rebuild for ocaml-lablgtk 2.18.

* Mon Sep 16 2013 Jerry James <loganjerry@gmail.com> - 1.9-7
- Rebuild for OCaml 4.01.0
- Enable debuginfo

* Fri Aug  9 2013 Jerry James <loganjerry@gmail.com> - 1.9-6
- Update -fixes patch to fix startup failures on ARM

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 21 2013 Jerry James <loganjerry@gmail.com> - 1.9-4
- Update to 20130601 bugfix Fluorine release

* Mon Jun  3 2013 Jerry James <loganjerry@gmail.com> - 1.9-3
- Add -fixes patch to fix code generation for inductive definitions

* Thu May 23 2013 Jerry James <loganjerry@gmail.com> - 1.9-2
- Update to bugfix Fluorine release

* Tue May 14 2013 Jerry James <loganjerry@gmail.com> - 1.9-1
- Update to Fluorine version
- Merge -devel into the main package (bz 888865)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 14 2013 Jerry James <loganjerry@gmail.com> - 1.8-5
- Rebuild for coq 8.4pl1 and alt-ergo 0.95

* Mon Nov  5 2012 Jerry James <loganjerry@gmail.com> - 1.8-4
- Build with zarith support

* Mon Oct 22 2012 Jerry James <loganjerry@gmail.com> - 1.8-3
- Update the Requires filter even more for Oxygen

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

* Sat Jul 17 2010 Mark Rader <msrader@gmail.com> 1.5-1
- Upgraded Frama C to Boron version and added ltl2ba dependencies.

* Mon Jul 05 2010 Mark Rader <msrader@gmail.com> 1.4-4
- Modified spec file to add new OCAML dependency structure for FC-13

* Sun Jun 06 2010 Mark Rader <msrader@gmail.com> 1.4-3
- Added documentation to explain the various licensing entries.
- Added .desktop file

* Wed May 26 2010 Mark Rader <msrader@gmail.com> 1.4-2
- Add SELinux context settings.

* Wed Feb 10 2010 Alan Dunn <amdunn@gmail.com> 1.4-1
- Initial Fedora RPM
