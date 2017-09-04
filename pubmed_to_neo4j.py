# written by ron weiner 

from Bio import Entrez
from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))


def search(query):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax='2000000000',
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


def split(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs

if __name__ == '__main__':
    journal_name='nature'
    results = search('1900[PDAT]:2020[PDAT],'+journal_name+'[JOURNAL]')
    id_list = results['IdList']
    print(len(id_list))

    session = driver.session()

    lastname = ""
    forename = ""
    initials = ""
    title = ""
    year = ""
    afname = ""

    if (len(id_list) > 0):
        id_list_b = split(id_list, 9000)


        session.run("MERGE (j:journal {title: {title}})",
                {"title": journal_name})
        for part_list in id_list_b:
            papers = fetch_details(part_list)


            for i, paper in enumerate(papers['PubmedArticle']):
                #the api lets you import 10,000 record each time, so i made a sleep function for 3 minutes each iteration
                print(i)
                #print("%d) %s" % (i + 1, paper['MedlineCitation']['Article']['ArticleTitle']))
                title=str(paper['MedlineCitation']['Article']['ArticleTitle'].encode('utf-8')).lower()
                paperDate = paper['MedlineCitation']['Article']['ArticleDate']
                if(len(paperDate)==0):
                    try:
                        #print(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])
                        year=paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
                    except KeyError:
                        #print("No Journal Year")
                        year = 0
                else:
                    for paperYear in enumerate(paperDate):
                        #print("%d) %s" % (i + 1, paperYear[1]['Year']))
                        year=paperYear[1]['Year']

                session.run("MERGE (b:article {title: {title}, year: {year}, article_id: {article_id}})",
                            {"title": title, "year": str(year),"article_id": str(part_list[i])})

                session.run(
                    "MATCH (j:journal {title: {titlej}}) , (b:article {article_id:{article_id}}) CREATE UNIQUE (b)-[:WAS_PUBLISHED_AT]->(j)",
                    {"titlej": journal_name, "article_id": str(part_list[i])})

                try:
                    authorList = paper['MedlineCitation']['Article']['AuthorList']
                except KeyError:
                    print("No Artist List")
                    continue

                for author in authorList:
                    try:
                        #print ("%d) %s" % (i + 1, "LastName: %s , Forename: %s , Initials: %s" % (
                        #author['LastName'], author['ForeName'], author['Initials'])))
                        lastname = str(author['LastName'].encode('utf-8')).lower()
                        forename =  str(author['ForeName'].encode('utf-8')).lower()
                        initials = str(author['Initials'].encode('utf-8')).lower()

                        session.run("MERGE (a:author {lastname: {lastname}, forename: {forename}, initials: {initials}})",
                                    {"lastname": lastname, "forename": forename, "initials": initials})

                        try:
                            #print("Affiliation: %s" % (author['AffiliationInfo'][0]['Affiliation']))
                            afname=str(author['AffiliationInfo'][0]['Affiliation'].encode('utf-8')).lower()

                            session.run("MERGE (c:affiliation {afname: {afname}})",
                                        {"afname": afname})

                            session.run(
                                "MATCH (a:author {lastname: {lastname}, forename: {forename}, initials: {initials}}) , (r:affiliation {afname:{afname}}) CREATE UNIQUE (a)-[:HAS_AFFILIATION]->(r)",
                                {"lastname": lastname, "forename": forename, "initials": initials, "afname": afname})

                        except (IndexError,KeyError):
                            #print("No Affiliation")
                            afname=str("No Affiliation")

                        #end of affiliation import

                        session.run(
                            "MATCH (a:author {lastname: {lastname}, forename: {forename}, initials: {initials}}) , (ar:article {article_id: {article_id}}) CREATE UNIQUE (a)-[:PARTICIPATE]->(ar)",
                            {"lastname": lastname, "forename": forename, "initials": initials,
                             "article_id": str(part_list[i])})

                    except KeyError:
                        print("No Author name")

    else:
        print("No ID")
    session.close()
