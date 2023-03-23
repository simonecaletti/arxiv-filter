import os
import time
import re
from datetime import datetime 
from pytz import timezone
import requests
import arxiv
from dotenv import load_dotenv

load_dotenv()

class Query(object):
    def __init__(self, result):
        self.date = result.updated
        self.url = result.entry_id
        self.title = result.title
        self.authors = ', '.join([author.name for author in result.authors])
        self.abstract = result.summary
        # self.date_str = query['published']
        self.id = result.entry_id[result.entry_id.find("/v")+5:]
        self.categories = result.categories

    @property
    def is_recent(self):
        curr_time = datetime.now(timezone('GMT'))
        delta_time = curr_time - self.date
        assert delta_time.total_seconds() > 0
        return delta_time.days < 2

    def __hash__(self):
        return self.id

    def __str__(self):
        s = ''
        s += self.title + '\n'
        s += self.url + '\n'
        s += self.authors + '\n'
        s += ', '.join(self.categories) + '\n'
        s += self.date.ctime() + ' GMT \n'
        s += '\n' + self.abstract + '\n'
        return s
    
    def printQuery(self):
      print("============")
      print(self.date)
      print(self.url)
      print("Title:", self.title)
      print("Authors:", self.authors)

class ArxivFilter(object):
  def __init__(self, categories, titles, authors):
    self._categories = categories
    self._titles = titles
    self._authors = authors

  @property
  def _get_previously_sent_arxivs(self, _prev_arxivs="prev_arxiv.txt"):
      if os.path.exists(_prev_arxivs):
          print("prev_arxiv.txt file does exist!")
          with open(_prev_arxivs, 'r') as f:
              return set(f.read().split('\n'))
      else:
          return set()

  def _save_previously_sent_arxivs(self, _new_queries, _prev_arxivs=".prev_arxiv.txt"):
      prev_arxivs = list(_get_previously_sent_arxivs(_prev_arxivs))
      prev_arxivs += [q.id for q in _new_queries]
      prev_arxivs = list(set(prev_arxivs))
      with open(_prev_arxivs, 'w') as f:
          f.write('\n'.join(prev_arxivs))

  def _get_queries_from_last_day(self, max_results=100):
        queries1 = []
        queries2 = []

        category_query_string = "OR ".join([f"cat:{category} " for category in self._categories]).strip()
        title_query_string = "OR ".join([f"ti:\"{title}\" " for title in self._titles]).strip()
        auth_query_string = "OR ".join([f"au:\"{author}\" " for author in self._authors]).strip()
        query_string1 = f"({category_query_string}) AND ({title_query_string})"
        query_string2 = f"({category_query_string}) AND ({auth_query_string})"
        #print("Query string 1: ", query_string1)
        #print("Query string 2", query_string2)

        # get all queries in the categories in the last day filtered by title keywords
        search1 = arxiv.Search(query=query_string1, sort_by=arxiv.SortCriterion.SubmittedDate, max_results=max_results)
        new_queries1 = [Query(result) for result in search1.results()]
        queries1 += [q for q in new_queries1 if q.is_recent]

        # get all queries in the categories in the last day filtered by author keywords
        search2 = arxiv.Search(query=query_string2, sort_by=arxiv.SortCriterion.SubmittedDate, max_results=max_results)
        new_queries2 = [Query(result) for result in search2.results()]
        queries2 += [q for q in new_queries2 if q.is_recent]

        # merge the two queries and get rid of duplicates
        queries = queries1 + queries2
        queries_dict = {q.id: q for q in queries}
        unique_keys = set(queries_dict.keys())
        unique_queries = [queries_dict[k] for k in unique_keys]

        # sort from most recent to least
        sorted_queries = sorted(unique_queries, key=lambda q: (datetime.now(timezone('GMT')) - q.date).total_seconds())

        # filter if previously sent
        prev_arxivs = _get_previously_sent_arxivs()
        prev_filtered_queries = [q for q in sorted_queries if q.id not in prev_arxivs]
        _save_previously_sent_arxivs(prev_filtered_queries)
        
        return prev_filtered_queries 
    
  def run(self):
    queries = self._get_queries_from_last_day()
    for q in queries:
      printQuery(q)

with open('categories.txt', 'r') as f:
  categories = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]

with open('titles.txt', 'r') as f:
  titles = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]

with open('authors.txt', 'r') as f:
  authors = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]

af = ArxivFilter(categories=categories,
                 titles=titles,
                 authors=authors)
af.run()