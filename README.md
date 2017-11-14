# Pubmed_to_Neo4j

--This research is still ongoing, no insights yet--

Thanks to friends (O.H and A.T) we saw that there is no code to import bulk data from Pubmed and manipulate it easily.
We wanted to see if there are any interesting patterns of the authors per each journal.
Decided to use graphdb to explore the main hops by the universities, affilitaions, name.

This code import the metadata of all the article ever published in a specific journal from pubmed repository.
Loads to a local graphdb (neo4j) the entities and relations of:
entities:
  1. journal (name)
  2. article(id,title,year of publish)
  3. author (first name,fore name, initials)
relations:
  1. author - HAS_AFFILIATION - affiliation
  2. article - WAS_PUBLISHED_AT - journal
  3. author - PARTICIPATE - article
  
Further possible exploration:
- connect to social platform and extract more information about the authors.
- add locations of universities

  cheers,
  ron weiner
