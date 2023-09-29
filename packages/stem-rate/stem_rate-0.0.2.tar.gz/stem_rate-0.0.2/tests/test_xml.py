# SPDX-FileCopyrightText: 2023-present Wytamma Wirth <wytamma.wirth@me.com>
#
# SPDX-License-Identifier: MIT
from stem_rate import BeastXML

# pytest for BeastXML class


def test_get_taxon_names():
    xml = BeastXML("tests/data/test.xml")
    assert xml.get_taxon_names() == ["A", "B", "C"]

def test_get_taxa_count():
    xml = BeastXML("tests/data/test.xml")
    assert xml.get_taxa_count() == 3

def test_taxa():
    xml = BeastXML("tests/data/test.xml")
    assert xml.taxa.tag == "taxa"

def test_write(tmp_path):
    xml = BeastXML("tests/data/test.xml")
    xml.write(tmp_path / "test.xml")
    assert (tmp_path / "test.xml").exists()

def test_insert_after():
    xml = BeastXML("tests/data/test.xml")
    xml.insert_after(xml.taxa, xml.taxa)
    # check there are 2 taxa elements
    assert len(xml.root.findall("taxa")) == 2

def test_create_stem_group():
    xml = BeastXML("tests/data/test.xml")
    test_group = xml.create_stem_group("A")
    xml.insert_after(xml.taxa, test_group)
    # check there are 2 taxa elements
    assert len(xml.root.findall("taxa")) == 2
    # check there are 1 taxa in the test taxa element
    assert len(test_group.findall("taxon")) == 1

def test_add_group_to_starting_tree():
    xml = BeastXML("tests/data/test.xml")
    a = xml.create_coalescent_simulator("A")
    xml.add_to_starting_tree(a)
    # check there are 1 taxa in the test taxa element
    assert len(xml.root.findall("coalescentSimulator/coalescentSimulator/taxa")) == 1
    # check there are 1 taxa in the test taxa element
    assert len(xml.root.findall("coalescentSimulator/coalescentSimulator/exponentialGrowth")) == 1

def test_create_tmraca_statistic():
    xml = BeastXML("tests/data/test.xml")
    tmraca = xml.create_tmraca_statistic("A")
    xml.add_tree_statistic(tmraca)
    # check there are 1 taxa in the test taxa element
    assert len(xml.root.findall("tmrcaStatistic")) == 2

def test_create_monophyly_statistic():
    xml = BeastXML("tests/data/test.xml")
    monophyly = xml.create_monophyly_statistic("A")
    xml.add_tree_statistic(monophyly)
    # check there are 1 taxa in the test taxa element
    assert len(xml.root.findall("monophylyStatistic")) == 1

def test_remove_element_by_id():
    xml = BeastXML("tests/data/test.xml")
    xml.remove_element_by_id("A")
    # check there are 1 taxa in the test taxa element
    assert len(xml.root.findall("taxa/taxon")) == 2

def test_create_local_clock():
    xml = BeastXML("tests/data/test.xml")
    test_group = xml.create_stem_group("A")
    xml.insert_after(xml.taxa, test_group)
    local_clock = xml.local_clock
    xml.add_local_clock(local_clock)

def test_replace_tag():
    xml = BeastXML("tests/data/test.xml")
    xml.replace_tag("taxa", "test")
    assert xml.root.find("test") is not None
    assert xml.root.find("taxa") is None

def test_replace():
    xml = BeastXML("tests/data/test.xml")
    test_el = xml.create_element("test", {})
    xml.replace(xml.taxa, test_el)
    # check there are 2 taxa elements
    assert len(xml.root.findall("test")) == 1

def test_rate_statistic():
    xml = BeastXML("tests/data/test.xml")
    cov = xml.coefficient_of_variation_statistic
    xml.add_rate_statistic(cov)
    assert xml.get_by_id("coefficientOfVariation") is not None
    cov = xml.rate_covariance_statistic
    xml.add_rate_statistic(cov)
    assert xml.get_by_id("covariance") is not None

def test_operators():
    xml = BeastXML("tests/data/test.xml")
    test_group = xml.create_stem_group("A")
    xml.insert_after(xml.taxa, test_group)
    for operator in xml.operators:
        xml.add_operator(operator)
    assert xml.get_by_idref("A.rate") is not None

def test_priors():
    xml = BeastXML("tests/data/test.xml")
    test_group = xml.create_stem_group("A")
    xml.insert_after(xml.taxa, test_group)
    for prior in xml.priors:
        xml.add_prior(prior)
    assert xml.get_by_idref("A.rate") is not None

def test_update_log():
    xml = BeastXML("tests/data/test.xml")
    test_group = xml.create_stem_group("A")
    xml.insert_after(xml.taxa, test_group)
    xml.update_log()
    assert xml.get_by_idref("A.rate") is not None

def test_add_fasta():
    xml = BeastXML("tests/data/test.xml")
    xml.add_fasta("tests/data/test.fasta")
    assert xml.get_taxa_count() == 4
    assert xml.get_taxon_names() == ["A|2023", "B|2023", "C|2023", "D|2023"]
    xml.write("test.fasta.xml")