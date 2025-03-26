import os
import requests
import numpy as np
from bs4 import BeautifulSoup
from sklearn.cluster import DBSCAN
from datasketch import MinHash
from collections import defaultdict
from urllib.parse import urljoin
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import concurrent.futures

class ProjUtils:
    def __init__(self, plot):
        self.plot = plot

    def group_documents(self, directory):
        docs = self.preprocess_all_html(directory)
        if not docs:
            return []
        
        similarity_matrix = self.compute_similarity_matrix(docs)
        labels = self.cluster_documents(similarity_matrix)

        if self.plot > 0:
            self.plot_tsne_clusters(similarity_matrix, labels, list(docs.keys()))
        
        clusters = defaultdict(list)
        for file, label in zip(docs.keys(), labels):
            clusters[label].append(os.path.basename(file))
        
        return [cluster for cluster in clusters.values() if len(cluster) >= 1]

    def preprocess_html(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')

        base_tag = soup.find('base', href=True)
        base_url = base_tag['href'] if base_tag else None

        text = self.extract_visible_text(soup)

        styles = self.extract_styles(soup, base_url)

        return {
            'text': text,
            'styles': styles,
            'file': os.path.basename(file_path)
        }

    def extract_visible_text(self, soup):
        # removing the tags since they are not visible for the user
        for script_or_style in soup(['script', 'style', 'noscript', 'iframe']):
            script_or_style.decompose()
    
        text = soup.get_text(separator=' ').lower()
        return " ".join(text.split())

    def extract_styles(self, soup, base_url=None):
        styles = []
        
        for tag in soup.find_all(attrs={"style": True}):
            style = tag['style']
            styles.append(self.normalize_css(style))

        for style_tag in soup.find_all('style'):
            if style_tag.string:
                styles.append(self.normalize_css(style_tag.string))

        stylesheets = [link['href'] for link in soup.find_all('link', rel='stylesheet') if 'href' in link.attrs]
        for css_url in stylesheets:
            if css_url:
                css_content = self.fetch_css(css_url, base_url)
                if css_content:
                    #print(f"Got {css_url}")
                    styles.append(self.normalize_css(css_content))

        return ' '.join(styles)

    def fetch_css(self, url, base_url=None):
        try:
            if url.startswith('//'):
                url = f"https:{url}"
            elif url.startswith('/') and base_url:
                url = urljoin(base_url, url)
            
            if not url.startswith(('http://', 'https://')):
                return None

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Referer": base_url or url
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text if response.text.strip() else None
        except requests.RequestException as e:
            #print(f"Failed css {url}: {e}")
            return None
        except ValueError as e:
            #print(f"Failed url {url}: {e}")
            return None

    def normalize_css(self, css):
        rules = css.split(';')
        normalized_rules = sorted([rule.strip() for rule in rules if rule.strip()])
        return ';'.join(normalized_rules)

    def compute_similarity_matrix(self, docs):
        minhashes = []
        
        # after testing with different values I considered this to be the most optimal weight for text
        text_weight = 0.88
        
        for doc in docs.values():
            mh = MinHash(num_perm=256)
            
            for word in doc['text'].split():
                mh.update(word.encode('utf-8'))
                
            for word in doc['styles'].split():
                mh.update(word.encode('utf-8'))
                
            minhashes.append(mh)
        
        n = len(minhashes)
        jaccard_matrix = np.array([[minhashes[i].jaccard(minhashes[j]) for j in range(n)] for i in range(n)])

        distance_matrix = (1 - jaccard_matrix) * text_weight

        return distance_matrix

    def cluster_documents(self, distance_matrix):
        dbscan = DBSCAN(metric='precomputed', eps=0.6, min_samples=1)
        labels = dbscan.fit_predict(distance_matrix)
        return labels

    def plot_tsne_clusters(self, distance_matrix, labels, filenames):
        tsne = TSNE(n_components=2, metric="precomputed", perplexity=5, random_state=42, init="random")
        reduced_data = tsne.fit_transform(distance_matrix)

        plt.figure(figsize=(6, 4))
        scatter = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='rainbow', alpha=0.7)
        plt.colorbar(scatter, label="Cluster")

        for i, filename in enumerate(filenames):
            plt.annotate(filename, (reduced_data[i, 0], reduced_data[i, 1]), fontsize=9, alpha=0.7)

        plt.title("Grouped Clusters")
        plt.show()

    def preprocess_all_html(self, directory, max_workers=4):
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.html')]
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.preprocess_html, file): file for file in files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results[result['file']] = result
                except Exception as e:
                    print(f"Error processing {file}: {e}")
        
        return results