# Veiridon's Deeptech Challenge: #5 HTML Clones

## Introduction
* From the list containing 5 tasks, I have chosen the fifth one because it sounded interesting and in my opinion could be a real-world challenge too. Also I'm passionate about every aspect of web based projects.

### Task description
* Design an algorithm that will group together HTML documents which are similar from the perspective of a user who opens them in a web browser.

### Resources
* A dataset containing lists of company websites, grouped by difficulties

### Output
* Your program should take one subdirectory at a time and output the grouped documents, something along the lines of: [A.html, B.html], [C.html], [D.html, E.html, F.html] etc.

## How to run the project
* Clone the project locally
* Install project's `requirements` ( pip install -r requirements.txt )
* Run `main.py` and a GUI will be shown

## The Thought process 
### Analyzing the Resources
* Before going into the actual coding I took some time to analyze manually the HTML files alongside with CSS styles + CSS urls and I noticed that a lot of CSS is unused in some cases and some of the CSS urls are down, not working or the `href` attribute in the HTML tag is broken so I decided to fix the urls if broken for fetching even the CSS from urls because it may contain data that the HTMLs don't provide and could change the page aspect seen by the end user.
* In order to parse the HTMLs and CSS styles I used python's package `BeautifulSoup`.
* For CSS urls styles fetching I started by retrieving the `href` attributes found in HTMLs and then fetching the urls using `requests`. This is where I found my first problem, some urls denied the requests made through python, despite working in a normal browser. Then I decided to send in the requests some headers ( User-Agetn and Referer ) which worked and I could retrieve the CSS contents.
* After solving the HTML and CSS parsing I needed to filter the content. I filtered any HTML tags that a normal user wouldn't see on page, keeping only the text and for CSS, filtered the attributes and removed extra whitespaces.

Example of CSS non-filtered style:
</br><img src="https://i.imgur.com/aqhx1Vl.png" alt="css_nonfilter_example" style="width: 50%; height: 50%"></img>

### Implementing the soultion
* In order to solve this challenge, I chose to use a ML algorithm for clusterization. After trying with HDBSCAN, OPTICS and DBSCAN I decided to go with DBSCAN because:
  * HDBSCAN is searching over varying epsilon values which uses more memory and runs longer
  * OPTICS's automatic technique ( xi ) was not accurate and the alogithm itself didn't allow clusters with only one point
  * DBSCAN fits the best because I can calculate the distance matrix, the clusters can contain even one point ( and yes, I know it performs O(n^2) but in my tests performed better than HDBSCAN ). Overall I was happy with this algorithm for solving the problem.

### Calculating the distance matrix
* To obtain a distance matrix within sets I came with a plan:
  * Used `MinHash` ( with a number of 256 permutations for more accurate hashes ) to approximate Jaccard similarity instead of directly computing the intersecion and union ( which is computationally hard for large datasets ) of the sets.
  * The next step is computing the hashes of each document, it goes through every `text` and `style` from it and generating signatures for every word and css attribute.
  * After all of that, I calculated the Jaccard matrix using the signatures for every words + styles generated for each document.
  * To calculate the distance matrix within points, I inverted the Jaccard matrix to get the distance measure of the points. I added text weights to the matrix so it will adjusts the importance of the text similarity between documents ( I tried with CSS too, but some document styles had way more CSS than others, unused and the solution is not accurate enough, considering for future problems tho ).

### Clustering from distance matrix using DBSCAN
* After calculating the distance matrix it is time to pass it to the clustering algorithm.
* At this I just had to find the optimal hyperparameters and after a long time I came to the current params:
  * metric = "precomputed" since the input is a distance matrix which is squared, this is the only way
  * eps ( epsilon ) = 0.6 which from my testing it's the best fit ( the maximum distance between two samples for one to be considered neighbours )
  * min_samples = 1 ( the number of samples in a cluster for a point to be considered a core point )

## Correctness
* The output of the solution is promising, having an estimated accuracy of over 95% ( maybe, I  calculated the correct similarities / total websites :) )

## The Extra mile
* Because I like my projects to handle large datasets / databases entries, I am always looking to improve the scalability, so I used thread concurency to process all documents faster.
* I added a diagram to plot points within the distance matrix.
* Because I wanted to push myself to do some frontend work, I implemented a GUI for the end user:
  * A button which allows to select the dataset directory
  * A button to plot the clusters visualization for every folder within the dataset
  * A button to start processing the data
  * A textarea showing the similar websites within every folder of the dataset
  * A button to export the results to a JSON file.

### GUI Preview
<img src="https://i.imgur.com/oBXwLWH.png" alt="gui_preview" style="width: 50%; height: 50%"></img>

### Clusters Plot Preview
<img src="https://i.imgur.com/S8U6bMK.png"  alt="clusters_plot_preview" style="width: 50%; height: 50%"></img>

### Websites grouped JSON file
https://github.com/ShadowsAdi/VeiridonChallenge/blob/master/exported_grouped_htmls.json

## Last thoughts
* I enjoyed this challenge and I am pretty happy with the results even if there is more room for improvement and my thought is what does Veridion behind the scenes because I think it could be very interesting.
