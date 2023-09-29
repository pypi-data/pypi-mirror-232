# SPDX-FileCopyrightText: 2023-present Wytamma Wirth <wytamma.wirth@me.com>
#
# SPDX-License-Identifier: MIT
import xml.etree.ElementTree as ET


def build_parent_map(root):
    return {c: p for p in root.iter() for c in p}

def get_parent(element, parent_map):
    return parent_map.get(element, None)

class BeastXML:
    def __init__(self, xml):
        self.xml = xml
        self.tree = ET.parse(xml)

    @property
    def root(self):
        return self.tree.getroot()

    @property
    def taxa(self):
        return self.root.find("taxa")

    @property
    def parent_map(self):
        return build_parent_map(self.root)

    def insert_after(self, element, after):
        parent = get_parent(element, self.parent_map)

        if parent is None:
            msg = "Parent not found"
            raise ValueError(msg)

        children = list(parent)
        index = children.index(element)

        parent.insert(index + 1, after)

    def create_element(self, tag: str, attrib: dict):
        return ET.Element(tag, attrib)

    def add_taxon(self, taxa, name, date_delimiter, date_position, date_units):
        taxon = self.create_element("taxon", {"id": name})
        date_value = name.split(date_delimiter)[date_position]
        date = self.create_element("date", {"value": date_value, "direction": "forwards", "units": date_units})
        taxon.append(date)
        taxa.append(taxon)

    def add_sequence(self, alignment, name, dna):
        sequence = self.create_element("sequence", {})
        taxon = self.create_element("taxon", {"idref": name})
        sequence.append(taxon)
        sequence.text = "".join(dna)
        alignment.append(sequence)

    def add_fasta(self, fasta, date_delimiter: str = "|", date_position: int = -1, date_units: str = "years"):
        taxa = self.create_element("taxa", {"id": "taxa"})
        alignment = self.create_element("alignment", {"id": "alignment", "dataType": "nucleotide"})

        with open(fasta) as f:
            name, dna = None, []
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if name:
                        self.add_taxon(taxa, name, date_delimiter, date_position, date_units)
                        self.add_sequence(alignment, name, dna)
                    name = line[1:]
                    dna = []
                else:
                    dna.append(line)

            if name:
                self.add_taxon(taxa, name, date_delimiter, date_position, date_units)
                self.add_sequence(alignment, name, dna)

        if self.taxa is not None:
            self.replace(self.taxa, taxa)
        else:
            # insert to beast at 0 index
            self.root.find("beast").insert(0, taxa)

        if self.get_by_id("alignment") is not None:
            self.replace(self.get_by_id("alignment"), alignment)
        else:
            # insert to beast at 0 index
            self.insert_after(self.taxa, alignment)



    def replace(self, target, replace_with):
        parent = get_parent(target, self.parent_map)

        if parent is None:
            msg = "Parent not found"
            raise ValueError(msg)

        children = list(parent)
        index = children.index(target)

        parent.insert(index + 1, replace_with)
        parent.remove(target)

    def create_stem_group(self, query):
        taxa_group = self.create_element("taxa", {"id": query})
        for taxon in self.taxa:
            if query not in taxon.attrib["id"]:
                continue
            taxa_group.append(self.create_element("taxon", {"idref": taxon.attrib["id"]}))
        return taxa_group

    def create_coalescent_simulator(self, stem: str):
        coalescent_simulator = self.create_element("coalescentSimulator", {})
        growth_el = self.create_element("exponentialGrowth", {"idref": "exponential"})
        taxa_ref = self.create_element("taxa", {"idref": stem})

        # append taxa_ref & growth_el to coalescentSimulator
        coalescent_simulator.append(taxa_ref)
        coalescent_simulator.append(growth_el)

        return coalescent_simulator

    def add_to_starting_tree(self, element: ET.Element):
        # prepend coalescentSimulator to startingTree
        starting_tree = self.get_by_id("startingTree")
        starting_tree.insert(0, element)

    def create_tmraca_statistic(self, stem: str):
        tmraca_statistic = self.create_element("tmrcaStatistic", {"id": f"tmrca({stem})", "absolute": "false", "includeStem": "false"})
        mrca = self.create_element("mrca", {})
        taxa_el = self.create_element("taxa", {"idref": stem})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        mrca.append(taxa_el)
        mrca.append(tree_model)
        tmraca_statistic.append(mrca)
        tmraca_statistic.append(tree_model)
        return tmraca_statistic

    def create_age_statistic(self, stem: str):
        tmraca_statistic = self.create_element("tmrcaStatistic", {"id": f"age({stem})", "absolute": "true", "includeStem": "false"})
        mrca = self.create_element("mrca", {})
        taxa_el = self.create_element("taxa", {"idref": stem})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        mrca.append(taxa_el)
        mrca.append(tree_model)
        tmraca_statistic.append(mrca)
        tmraca_statistic.append(tree_model)
        return tmraca_statistic

    def create_monophyly_statistic(self, stem: str):
        monophyly_statistic = self.create_element("monophylyStatistic", {"id": f"monophyly({stem})"})
        mrca = self.create_element("mrca", {})
        taxa_el = self.create_element("taxa", {"idref": stem})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        mrca.append(taxa_el)
        mrca.append(tree_model)
        monophyly_statistic.append(mrca)
        monophyly_statistic.append(tree_model)
        return monophyly_statistic

    @property
    def tree_statistics(self):
        stem_names = self.stem_names
        statistics = []
        for stem_name in stem_names:
            statistics.append(self.create_tmraca_statistic(stem_name))
            statistics.append(self.create_age_statistic(stem_name))
            statistics.append(self.create_monophyly_statistic(stem_name))
        return statistics

    def add_tree_statistic(self, element: ET.Element):
        tree_model = self.root.find("treeModel")
        self.insert_after(tree_model, element)

    @property
    def local_clock(self):
        local_clock = self.create_element("localClockModel", {"id": "branchRates"})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        rate = self.create_element("rate", {})
        parameter = self.create_element("parameter", {"id": "clock.rate", "value": "1.0", "lower": "0.0"})
        rate.append(parameter)
        local_clock.append(tree_model)
        local_clock.append(rate)
        stem_names = self.stem_names
        for stem_name in stem_names:
            clade = self.create_element("clade", {"includeStem": "true", "excludeClade": "true"})
            parameter = self.create_element("parameter", {"id": f"{stem_name}.rate", "value": "1.0", "lower": "0.0"})
            taxa = self.create_element("taxa", {"idref": stem_name})
            clade.append(parameter)
            clade.append(taxa)
            local_clock.append(clade)
        return local_clock

    def add_local_clock(self, clock: ET.Element, after: str = "branchRates"):
        old_model = self.get_by_id(after)
        # replace references to coalescent with localClockModel
        self.replace_tag(old_model.tag, clock.tag)
        self.insert_after(old_model, clock)
        self.remove_element_by_id(after)


    @property
    def coefficient_of_variation_statistic(self):
        """
        <rateStatistic id="coefficientOfVariation" name="coefficientOfVariation" mode="coefficientOfVariation" internal="true" external="true">
            <treeModel idref="treeModel"/>
            <localClockModel idref="branchRates"/>
        </rateStatistic>
        """
        rate_statistic = self.create_element("rateStatistic", {"id": "coefficientOfVariation", "name": "coefficientOfVariation", "mode": "coefficientOfVariation", "internal": "true", "external": "true"})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        local_clock = self.create_element("localClockModel", {"idref": "branchRates"})
        rate_statistic.append(tree_model)
        rate_statistic.append(local_clock)
        return rate_statistic

    @property
    def rate_covariance_statistic(self):
        """
        <rateCovarianceStatistic id="covariance" name="covariance">
            <treeModel idref="treeModel"/>
            <localClockModel idref="branchRates"/>
        </rateCovarianceStatistic>
        """
        rate_covariance_statistic = self.create_element("rateCovarianceStatistic", {"id": "covariance", "name": "covariance"})
        tree_model = self.create_element("treeModel", {"idref": "treeModel"})
        local_clock = self.create_element("localClockModel", {"idref": "branchRates"})
        rate_covariance_statistic.append(tree_model)
        rate_covariance_statistic.append(local_clock)
        return rate_covariance_statistic


    def add_rate_statistic(self, element: ET.Element):
        statistic = self.root.find("rateStatistic")
        self.insert_after(statistic, element)

    def create_rate_scale_operator(self, stem: str, weight: float = 3, scale: float = 0.75):
        """
        <scaleOperator scaleFactor="0.75" weight="3">
                <parameter idref="B117.rate"/>
        </scaleOperator>
        """
        operator = self.create_element("scaleOperator", {"scaleFactor": str(scale), "weight": str(weight)})
        parameter = self.create_element("parameter", {"idref": f"{stem}.rate"})
        operator.append(parameter)
        return operator

    @property
    def operators(self):
        stem_names = self.stem_names
        operators = []
        for stem_name in stem_names:
            operators.append(self.create_rate_scale_operator(stem_name))
        return operators

    def add_operator(self, element: ET.Element):
        operators = self.root.find("operators")
        operators.append(element)

    @property
    def priors(self):
        """
        <booleanLikelihood>
            <monophylyStatistic idref="monophyly(P1)"/>
            <monophylyStatistic idref="monophyly(B16172)"/>
            <monophylyStatistic idref="monophyly(B117)"/>
            <monophylyStatistic idref="monophyly(B1351)"/>
        </booleanLikelihood>
        <gammaPrior shape="0.5" scale="0.1" offset="0.0">
            <parameter idref="BA.2.86.rate"/>
        </gammaPrior>
        """
        stem_names = self.stem_names
        priors = []
        for stem_name in stem_names:
            prior = self.create_element("gammaPrior", {"shape": "0.5", "scale": "0.1", "offset": "0.0"})
            parameter = self.create_element("parameter", {"idref": f"{stem_name}.rate"})
            prior.append(parameter)
            priors.append(prior)
        boolean_likelihood = self.create_element("booleanLikelihood", {})
        for stem_name in self.stem_names:
            monophyly_statistic = self.create_element("monophylyStatistic", {"idref": f"monophyly({stem_name})"})
            boolean_likelihood.append(monophyly_statistic)
        priors.append(boolean_likelihood)
        return priors

    def add_prior(self, element: ET.Element):
        priors = self.get_by_id("prior")
        priors.append(element)

    def update_log(self):
        """
        <tmrcaStatistic idref="tmrca(B117)"/>
        <tmrcaStatistic idref="age(B117)"/>
        <parameter idref="B117.rate"/>
        <rateStatistic idref="coefficientOfVariation"/>
        <rateCovarianceStatistic idref="covariance"/>
        """
        file_log = self.get_by_id("fileLog")
        for stem_name in self.stem_names:
            file_log.append(self.create_element("parameter", {"idref": f"{stem_name}.rate"}))
            file_log.append(self.create_element("tmrcaStatistic", {"idref": f"tmrca({stem_name})"}))
            file_log.append(self.create_element("tmrcaStatistic", {"idref": f"age({stem_name})"}))
        file_log.append(self.create_element("rateStatistic", {"idref": "coefficientOfVariation"}))
        file_log.append(self.create_element("rateCovarianceStatistic", {"idref": "covariance"}))

    def replace_tag(self, tag: str, replace: str):
        for element in self.root.iter():
            if element.tag == tag:
                element.tag = replace

    def get_by_id(self, id: str):
        return self.root.find(f".//*[@id='{id}']")

    def get_by_idref(self, idref: str):
        return self.root.find(f".//*[@idref='{idref}']")

    def remove_element_by_id(self, id: str):
        element = self.get_by_id(id)
        parent = get_parent(element, self.parent_map)
        parent.remove(element)

    @property
    def stem_names(self):
        taxa = self.root.findall("taxa")
        if len(taxa) == 1:
            raise ValueError("No stems found")
        names = []
        for tax in taxa[1:]:
            names.append(tax.attrib["id"])
        return names

    def get_taxon_names(self):
        taxa = self.taxa
        names = []
        for taxon in taxa:
            names.append(taxon.attrib["id"])
        return names

    def get_taxa_count(self):
        return len(self.get_taxon_names())

    def prettify(self, elem):
        from xml.dom import minidom
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")

    def write(self, outfile):
        # Formatting manually
          # format xml
        xmlstr = "\n".join([line for line in self.prettify(self.root).split("\n") if line.strip()])
        with open(outfile, "w") as f:
            f.write(xmlstr)