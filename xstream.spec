%global pkg_name xstream
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Copyright statement from JPackage this file is derived from:

# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Tests are disabled by default since we don't have
# all the requirements in Fedora yet
%bcond_with test

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.3.1
Release:        9.13%{?dist}
Summary:        Java XML serialization library

License:        BSD
URL:            http://xstream.codehaus.org/
Source0:        http://repository.codehaus.org/com/thoughtworks/%{pkg_name}/%{pkg_name}-distribution/%{version}/%{pkg_name}-distribution-%{version}-src.zip

BuildRequires:  %{?scl_prefix_java_common}javapackages-tools
BuildRequires:  %{?scl_prefix_java_common}ant >= 0:1.6
BuildRequires:  %{?scl_prefix_java_common}bea-stax >= 0:1.2.0
BuildRequires:  %{?scl_prefix_java_common}bea-stax-api >= 0:1.0.1
BuildRequires:  maven30-cglib >= 0:2.1.3
BuildRequires:  %{?scl_prefix_java_common}dom4j >= 0:1.6.1
BuildRequires:  %{?scl_prefix_java_common}apache-commons-lang >= 0:2.1
BuildRequires:  %{?scl_prefix_java_common}jakarta-oro
BuildRequires:  %{?scl_prefix_java_common}jdom >= 0:1.0
BuildRequires:  maven30-jettison >= 0:1.0
BuildRequires:  maven30-joda-time >= 0:1.2.1
BuildRequires:  %{?scl_prefix_java_common}junit >= 0:3.8.1
BuildRequires:  %{?scl_prefix_java_common}xpp3 >= 0:1.1.3.4
BuildRequires:  unzip
%if %with test
BuildRequires:  maven30-jmock >= 0:1.0.1
BuildRequires:  maven30-wstx >= 0:3.2.0
%endif
Requires:       %{?scl_prefix_java_common}xpp3-minimal

BuildArch:      noarch


%description
XStream is a simple library to serialize objects to XML 
and back again. A high level facade is supplied that 
simplifies common use cases. Custom objects can be serialized 
without need for specifying mappings. Speed and low memory 
footprint are a crucial part of the design, making it suitable 
for large object graphs or systems with high message throughput. 
No information is duplicated that can be obtained via reflection. 
This results in XML that is easier to read for humans and more 
compact than native Java serialization. XStream serializes internal 
fields, including private and final. Supports non-public and inner 
classes. Classes are not required to have default constructor. 
Duplicate references encountered in the object-model will be 
maintained. Supports circular references. By implementing an 
interface, XStream can serialize directly to/from any tree 
structure (not just XML). Strategies can be registered allowing 
customization of how particular types are represented as XML. 
When an exception occurs due to malformed XML, detailed diagnostics 
are provided to help isolate and fix the problem.


%package        javadoc
Summary:        Javadoc for %{pkg_name}

%description    javadoc
%{pkg_name} API documentation.

%package        benchmark
Summary:        benchmark module for %{pkg_name}
Requires:       %{name} = %{version}-%{release}

%description    benchmark
benchmark module for %{pkg_name}.


%prep
%setup -qn %{pkg_name}-%{version}
%{?scl:scl enable maven30 %{scl} - <<"EOF"}
set -e -x
find . -name "*.jar" -delete

%if %with test
# This test requires megginson's sax2
rm -f xstream/src/test/com/thoughtworks/xstream/io/xml/SaxWriterTest.java
%endif

find -name XomDriver.java -delete
find -name XomReader.java -delete
find -name XomWriter.java -delete
%{?scl:EOF}


%build
%{?scl:scl enable maven30 %{scl} - <<"EOF"}
set -e -x
# Replace bundled tars
pushd xstream/lib
ln -sf $(build-classpath cglib)
ln -sf $(build-classpath commons-lang)
ln -sf $(build-classpath dom4j)
ln -sf $(build-classpath jdom)
ln -sf $(build-classpath jettison)
ln -sf $(build-classpath joda-time)
ln -sf $(build-classpath junit)
ln -sf $(build-classpath oro)
ln -sf $(build-classpath bea-stax-ri)
ln -sf $(build-classpath bea-stax-api)
ln -sf $(build-classpath xpp3)
%if %with test
ln -sf $(build-classpath jmock)
ln -sf $(build-classpath wstx/wstx-asl)
%endif
popd

# Build
pushd xstream
%if %with test
ant library javadoc
%else
ant benchmark:compile jar javadoc
%endif
popd
%{?scl:EOF}


%install
%{?scl:scl enable maven30 %{scl} - <<"EOF"}
set -e -x

# Directory structure
install -d $RPM_BUILD_ROOT%{_javadir}
install -d $RPM_BUILD_ROOT%{_javadocdir}

# Main jar
pushd xstream
install -p -m644 target/xstream-SNAPSHOT.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}.jar

# Benchmarks
install -p -m644 target/xstream-benchmark-SNAPSHOT.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}-benchmark.jar

# API Documentation
cp -pr target/javadoc $RPM_BUILD_ROOT%{_javadocdir}/%{name}
popd

# POMs
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}-parent.pom
%add_maven_depmap JPP-%{pkg_name}-parent.pom

install -pm 644 xstream/pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}.pom
%add_maven_depmap

install -pm 644 xstream-benchmark/pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}-benchmark.pom
%add_maven_depmap JPP-%{pkg_name}-benchmark.pom %{pkg_name}-benchmark.jar -f benchmark
%{?scl:EOF}


%files -f .mfiles
%{_javadir}/%{pkg_name}.jar
%doc LICENSE.txt

%files benchmark -f .mfiles-benchmark
%{_javadir}/%{pkg_name}-benchmark.jar

%files javadoc
%{_javadocdir}/%{name}
%doc LICENSE.txt


%changelog
* Sat Jan 09 2016 Michal Srb <msrb@redhat.com> - 1.3.1-9.13
- maven33 rebuild

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.3.1-9.12
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michal Srb <msrb@redhat.com> - 1.3.1-9.11
- Fix BR/R

* Fri Jan 09 2015 Michal Srb <msrb@redhat.com> - 1.3.1-9.10
- Install correct POM for xstream-benchmark

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 1.3.1-9.9
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.8
- Mass rebuild 2014-05-26

* Fri Feb 28 2014 Michael Simacek <msimacek@redhat.com> - 1.3.1-9.7
- Split subpackage

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.5
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.4
- Remove requires on java

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.3
- SCL-ize requires and build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-9.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.3.1-9
- Mass rebuild 2013-12-27

* Wed Sep 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-8
- Disable support for XOM

* Fri Jul 12 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-7
- Update to current packaging guidelines

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-6
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jun 14 2010 Alexander Kurtakov <akurtako@redhat.com> 1.3.1-1
- Update to 1.3.1.
- Install maven pom and depmap.

* Wed Dec 02 2009 Lubomir Rintel <lkundrak@v3.sk> - 1.2.2-4
- Cosmetic fixes

* Fri Nov 27 2009 Lubomir Rintel <lkundrak@v3.sk> - 0:1.2.2-3
- Drop gcj (suggested by Jochen Schmitt), we seem to need OpenJDK anyway
- Fix -javadoc Require
- Drop epoch

* Sun Nov 01 2009 Lubomir Rintel <lkundrak@v3.sk> - 0:1.2.2-2
- Greatly simplify for Fedora
- Disable tests, we don't have all that's required to run them
- Remove maven build

* Fri Jul 20 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.2.2-1jpp
- Upgrade to 1.2.2
- Build with maven2 by default
- Add poms and depmap frags

* Tue May 23 2006 Ralph Apel <r.apel at r-apel.de> - 0:1.1.3-1jpp
- Upgrade to 1.1.3
- Patched to work with bea

* Mon Sep 13 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.2-2jpp
- Drop saxpath requirement
- Require jaxen >= 0:1.1

* Mon Aug 30 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.2-1jpp
- Upgrade to 1.0.2
- Delete included binary jars
- Change -Dbuild.sysclasspath "from only" to "first" (DynamicProxyTest)
- Relax some versioned dependencies
- Build with ant-1.6.2

* Fri Aug 06 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.1-2jpp
- Upgrade to ant-1.6.X

* Tue Jun 01 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.1-1jpp
- Upgrade to 1.0.1

* Fri Feb 13 2004 Ralph Apel <r.apel at r-apel.de> - 0:0.3-1jpp
- Upgrade to 0.3
- Add manual subpackage

* Mon Jan 19 2004 Ralph Apel <r.apel at r-apel.de> - 0:0.2-1jpp
- First JPackage release
