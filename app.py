from flask import Flask, render_template_string, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import time
import csv
import io

app = Flask(__name__)

# Template HTML untuk UI
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraper with Pagination</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .input-group input:focus, .input-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .loading.active {
            display: block;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .results.active {
            display: block;
        }
        .result-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            color: #666;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        .tab-content.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .item-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .item-content {
            color: #666;
            word-break: break-all;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            opacity: 0.9;
        }
        .download-btn {
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
            font-weight: 600;
        }
        .download-btn:hover {
            background: #218838;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f5c6cb;
            margin-top: 20px;
        }
        .pagination-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .control-group {
            flex: 1;
            min-width: 200px;
        }
        .download-options {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .download-options select {
            margin-left: 10px;
            padding: 5px 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕷️ Web Scraper with Pagination</h1>
            <p>Ekstrak data dari website dengan pagination</p>
        </div>
        
        <div class="content">
            <form id="scraperForm">
                <div class="input-group">
                    <label for="url">URL Website</label>
                    <input type="url" id="url" name="url" placeholder="https://example.com" required>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label for="scrapeType">Tipe Data yang Ingin Diambil</label>
                        <select id="scrapeType" name="scrapeType">
                            <option value="all">Semua Data</option>
                            <option value="links">Links Saja</option>
                            <option value="images">Gambar Saja</option>
                            <option value="text">Teks Saja</option>
                            <option value="headings">Heading Saja</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="maxPages">Maksimal Halaman (0 untuk auto-detect)</label>
                        <input type="number" id="maxPages" name="maxPages" min="0" max="50" value="0">
                    </div>
                    
                    <div class="control-group">
                        <label for="pageDelay">Delay antar halaman (detik)</label>
                        <input type="number" id="pageDelay" name="pageDelay" min="0" max="10" step="0.5" value="1">
                    </div>
                </div>
                
                <div class="input-group">
                    <label>
                        <input type="checkbox" id="enablePagination" checked> Aktifkan Pagination Auto-detect
                    </label>
                </div>
                
                <button type="submit" class="btn" id="scrapeBtn">Mulai Scraping</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Sedang mengambil data...</p>
                <p id="loadingDetails"></p>
            </div>
            
            <div class="results" id="results">
                <div class="pagination-info" id="paginationInfo"></div>
                <div class="stats" id="stats"></div>
                
                <div class="result-tabs">
                    <button class="tab active" data-tab="links">Links</button>
                    <button class="tab" data-tab="images">Gambar</button>
                    <button class="tab" data-tab="text">Teks</button>
                    <button class="tab" data-tab="headings">Headings</button>
                </div>
                
                <div class="download-options" id="downloadOptions">
                    <strong>Download Options:</strong><br>
                    <button class="download-btn" onclick="downloadJSON()">📥 Download JSON</button>
                    <select id="csvType">
                        <option value="all">Semua Data</option>
                        <option value="links">Links</option>
                        <option value="images">Gambar</option>
                        <option value="text">Teks</option>
                        <option value="headings">Headings</option>
                    </select>
                    <button class="download-btn" onclick="downloadCSV()">📥 Download CSV</button>
                    <button class="download-btn" onclick="downloadAllPages()">📥 Download Semua Halaman</button>
                </div>
                
                <div class="tab-content active" id="links-content"></div>
                <div class="tab-content" id="images-content"></div>
                <div class="tab-content" id="text-content"></div>
                <div class="tab-content" id="headings-content"></div>
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        let scrapedData = null;
        let currentScrapeType = 'all';
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                this.classList.add('active');
                document.getElementById(this.dataset.tab + '-content').classList.add('active');
            });
        });
        
        // Form submission
        document.getElementById('scraperForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const scrapeType = document.getElementById('scrapeType').value;
            const maxPages = document.getElementById('maxPages').value;
            const pageDelay = document.getElementById('pageDelay').value;
            const enablePagination = document.getElementById('enablePagination').checked;
            
            // Save current scrape type
            currentScrapeType = scrapeType;
            
            // Show loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            document.getElementById('error').style.display = 'none';
            document.getElementById('scrapeBtn').disabled = true;
            document.getElementById('loadingDetails').textContent = 'Mengambil halaman 1...';
            
            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        url, 
                        scrapeType,
                        maxPages: parseInt(maxPages),
                        pageDelay: parseFloat(pageDelay),
                        enablePagination 
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                scrapedData = data;
                displayResults(data);
                
            } catch (error) {
                document.getElementById('error').textContent = 'Error: ' + error.message;
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('scrapeBtn').disabled = false;
            }
        });
        
        function displayResults(data) {
            // Pagination info
            const paginationInfo = document.getElementById('paginationInfo');
            if (data.total_pages > 1) {
                paginationInfo.innerHTML = '<strong>📄 Informasi Pagination:</strong><br>' +
                    '• Total halaman yang di-scrape: ' + data.total_pages + '<br>' +
                    '• Total waktu scraping: ' + data.total_time.toFixed(2) + ' detik<br>' +
                    '• URL dasar: ' + data.base_url + '<br>' +
                    '• Halaman terakhir: ' + (data.last_page_url || 'N/A');
                paginationInfo.style.display = 'block';
            } else {
                paginationInfo.style.display = 'none';
            }
            
            // Update CSV type selector based on scrape type
            const csvTypeSelect = document.getElementById('csvType');
            if (currentScrapeType !== 'all') {
                csvTypeSelect.value = currentScrapeType;
            }
            
            // Stats
            const stats = document.getElementById('stats');
            stats.innerHTML = '<div class="stat-card">' +
                '<div class="stat-number">' + data.links.length + '</div>' +
                '<div class="stat-label">Links</div>' +
                '</div>' +
                '<div class="stat-card">' +
                '<div class="stat-number">' + data.images.length + '</div>' +
                '<div class="stat-label">Gambar</div>' +
                '</div>' +
                '<div class="stat-card">' +
                '<div class="stat-number">' + data.paragraphs.length + '</div>' +
                '<div class="stat-label">Paragraf</div>' +
                '</div>' +
                '<div class="stat-card">' +
                '<div class="stat-number">' + data.headings.length + '</div>' +
                '<div class="stat-label">Headings</div>' +
                '</div>';
            
            // Links
            const linksContent = document.getElementById('links-content');
            if (data.links && data.links.length > 0) {
                let linksHtml = '';
                data.links.forEach(link => {
                    linksHtml += '<div class="item">' +
                        '<div class="item-title">' + (link.text || 'No text') + '</div>' +
                        '<div class="item-content">' + link.url + (link.page ? ' (Halaman ' + link.page + ')' : '') + '</div>' +
                        '</div>';
                });
                linksContent.innerHTML = linksHtml;
            } else {
                linksContent.innerHTML = '<p>Tidak ada link ditemukan</p>';
            }
            
            // Images
            const imagesContent = document.getElementById('images-content');
            if (data.images && data.images.length > 0) {
                let imagesHtml = '';
                data.images.forEach(img => {
                    imagesHtml += '<div class="item">' +
                        '<div class="item-title">' + (img.alt || 'No alt text') + '</div>' +
                        '<div class="item-content">' + img.src + (img.page ? ' (Halaman ' + img.page + ')' : '') + '</div>' +
                        '</div>';
                });
                imagesContent.innerHTML = imagesHtml;
            } else {
                imagesContent.innerHTML = '<p>Tidak ada gambar ditemukan</p>';
            }
            
            // Text
            const textContent = document.getElementById('text-content');
            if (data.paragraphs && data.paragraphs.length > 0) {
                let textHtml = '';
                data.paragraphs.forEach(text => {
                    textHtml += '<div class="item">' +
                        '<div class="item-content">' + text.content + (text.page ? ' (Halaman ' + text.page + ')' : '') + '</div>' +
                        '</div>';
                });
                textContent.innerHTML = textHtml;
            } else {
                textContent.innerHTML = '<p>Tidak ada teks ditemukan</p>';
            }
            
            // Headings
            const headingsContent = document.getElementById('headings-content');
            if (data.headings && data.headings.length > 0) {
                let headingsHtml = '';
                data.headings.forEach(h => {
                    headingsHtml += '<div class="item">' +
                        '<div class="item-title">' + h.level + '</div>' +
                        '<div class="item-content">' + h.text + (h.page ? ' (Halaman ' + h.page + ')' : '') + '</div>' +
                        '</div>';
                });
                headingsContent.innerHTML = headingsHtml;
            } else {
                headingsContent.innerHTML = '<p>Tidak ada heading ditemukan</p>';
            }
            
            document.getElementById('results').classList.add('active');
        }
        
        function downloadJSON() {
            // Create filtered data based on scrape type
            let filteredData = filterDataByType(scrapedData, currentScrapeType);
            
            const dataStr = JSON.stringify(filteredData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = getFileName('json');
            link.click();
        }
        
        function downloadCSV() {
            const csvType = document.getElementById('csvType').value;
            
            // Create filtered data based on selected CSV type
            let filteredData = filterDataByType(scrapedData, csvType);
            
            let csv = '';
            let filename = '';
            
            switch(csvType) {
                case 'links':
                    csv = 'Text,URL,Page\\n';
                    filteredData.links.forEach(link => {
                        csv += '"' + escapeCSV(link.text || '') + '","' + escapeCSV(link.url) + '","' + (link.page || 1) + '"\\n';
                    });
                    filename = 'links.csv';
                    break;
                    
                case 'images':
                    csv = 'Alt Text,Source URL,Page\\n';
                    filteredData.images.forEach(img => {
                        csv += '"' + escapeCSV(img.alt || '') + '","' + escapeCSV(img.src) + '","' + (img.page || 1) + '"\\n';
                    });
                    filename = 'images.csv';
                    break;
                    
                case 'text':
                    csv = 'Content,Page\\n';
                    filteredData.paragraphs.forEach(text => {
                        csv += '"' + escapeCSV(text.content) + '","' + (text.page || 1) + '"\\n';
                    });
                    filename = 'text.csv';
                    break;
                    
                case 'headings':
                    csv = 'Level,Content,Page\\n';
                    filteredData.headings.forEach(h => {
                        csv += '"' + escapeCSV(h.level) + '","' + escapeCSV(h.text) + '","' + (h.page || 1) + '"\\n';
                    });
                    filename = 'headings.csv';
                    break;
                    
                case 'all':
                default:
                    // Combined CSV
                    csv = 'Type,Content,URL/Alt/Level,Page\\n';
                    
                    // Add links
                    scrapedData.links.forEach(link => {
                        csv += 'Link,"' + escapeCSV(link.text || '') + '","' + escapeCSV(link.url) + '","' + (link.page || 1) + '"\\n';
                    });
                    
                    // Add images
                    scrapedData.images.forEach(img => {
                        csv += 'Image,"' + escapeCSV(img.alt || '') + '","' + escapeCSV(img.src) + '","' + (img.page || 1) + '"\\n';
                    });
                    
                    // Add text
                    scrapedData.paragraphs.forEach(text => {
                        csv += 'Text,"' + escapeCSV(text.content) + '","","' + (text.page || 1) + '"\\n';
                    });
                    
                    // Add headings
                    scrapedData.headings.forEach(h => {
                        csv += 'Heading,"' + escapeCSV(h.level) + '","' + escapeCSV(h.text) + '","' + (h.page || 1) + '"\\n';
                    });
                    
                    filename = 'all_data.csv';
                    break;
            }
            
            const dataBlob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.click();
        }
        
        function escapeCSV(str) {
            if (str === null || str === undefined) return '';
            return String(str).replace(/"/g, '""');
        }
        
        function filterDataByType(data, type) {
            // Create a deep copy of the data
            let filteredData = JSON.parse(JSON.stringify(data));
            
            switch(type) {
                case 'links':
                    filteredData.images = [];
                    filteredData.paragraphs = [];
                    filteredData.headings = [];
                    break;
                case 'images':
                    filteredData.links = [];
                    filteredData.paragraphs = [];
                    filteredData.headings = [];
                    break;
                case 'text':
                    filteredData.links = [];
                    filteredData.images = [];
                    filteredData.headings = [];
                    break;
                case 'headings':
                    filteredData.links = [];
                    filteredData.images = [];
                    filteredData.paragraphs = [];
                    break;
                case 'all':
                default:
                    // Keep all data
                    break;
            }
            
            return filteredData;
        }
        
        function getFileName(extension) {
            const typeMap = {
                'links': 'links',
                'images': 'images',
                'text': 'text',
                'headings': 'headings',
                'all': 'all_data'
            };
            
            const prefix = typeMap[currentScrapeType] || 'scraped';
            return prefix + '_' + new Date().toISOString().slice(0,10) + '.' + extension;
        }
        
        function downloadAllPages() {
            const pages = scrapedData.all_pages || [];
            let csv = 'Page,URL,Status\\n';
            pages.forEach(page => {
                csv += '"' + page.page_number + '","' + page.url + '","' + page.status + '"\\n';
            });
            
            const dataBlob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'all_pages.csv';
            link.click();
        }
    </script>
</body>
</html>'''

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.base_url = self._get_base_url(url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _get_base_url(self, url):
        """Extract base URL for constructing absolute URLs"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def fetch_page(self, url=None):
        """Fetch a single page"""
        try:
            target_url = url or self.url
            response = requests.get(
                target_url, 
                headers=self.headers, 
                timeout=15,
                verify=False
            )
            response.raise_for_status()
            return response.text, response.url
        except Exception as e:
            raise Exception(f"Error fetching page {url or self.url}: {str(e)}")
    
    def parse_html(self, html_content):
        return BeautifulSoup(html_content, 'html.parser')
    
    def detect_pagination(self, soup):
        """Detect pagination patterns in the page"""
        pagination_selectors = [
            # Common pagination selectors
            'nav.pagination',
            'ul.pagination',
            '.pagination',
            '.page-numbers',
            '.pager',
            '.pages',
            'nav[aria-label*="pagination"]',
            'nav[aria-label*="Pagination"]',
            '.pagination-nav',
            '.pagination-wrapper',
            # Next/prev links
            'a[rel="next"]',
            'a[rel="prev"]',
            'a:contains("Next")',
            'a:contains("next")',
            'a:contains(">")',
            'a:contains("»")',
            # Page number links
            'a[href*="page="]',
            'a[href*="p="]',
            'a[href*="/page/"]',
            'a.page-numbers',
            'a.page',
            'li.page',
            # Numerical pagination
            'a:contains("2")',
            'a:contains("3")',
            # Bootstrap pagination
            '.pagination li a',
            # Wordpress pagination
            '.nav-links a',
            '.wp-pagenavi a',
        ]
        
        pagination_links = []
        for selector in pagination_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if element.name == 'a' and element.get('href'):
                        href = element.get('href')
                        text = element.get_text(strip=True).lower()
                        
                        # Convert relative URLs to absolute
                        if not href.startswith(('http://', 'https://')):
                            href = urljoin(self.base_url, href)
                        
                        # Check if it's a pagination link
                        is_pagination = False
                        
                        # Check by text content
                        if any(keyword in text for keyword in ['next', '>', '»', 'older', 'newer', 'previous', '<', '«']):
                            is_pagination = True
                        
                        # Check by URL pattern
                        pagination_patterns = ['page=', 'p=', '/page/', '?p=', '&p=', 'paged=']
                        if any(pattern in href.lower() for pattern in pagination_patterns):
                            is_pagination = True
                        
                        # Check by numeric content
                        if text.isdigit() and 1 <= int(text) <= 100:
                            is_pagination = True
                        
                        if is_pagination and href not in [link['url'] for link in pagination_links]:
                            pagination_links.append({
                                'url': href,
                                'text': element.get_text(strip=True),
                                'type': 'next' if 'next' in text or '>' in text or '»' in text else 'page'
                            })
            except:
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in pagination_links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def extract_page_number(self, url):
        """Extract page number from URL"""
        patterns = [
            r'page[=/](\d+)',
            r'p[=/](\d+)',
            r'paged=(\d+)',
            r'/(\d+)/?$',
            r'\?.*?page=(\d+)',
            r'&page=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Check if URL ends with a number
        match = re.search(r'/(\d+)$', url)
        if match:
            return int(match.group(1))
        
        return None
    
    def extract_links(self, soup, page_number=1):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href.startswith(('http://', 'https://')):
                href = urljoin(self.base_url, href)
            
            links.append({
                'text': link.get_text(strip=True),
                'url': href,
                'page': page_number
            })
        return links
    
    def extract_images(self, soup, page_number=1):
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not src.startswith(('http://', 'https://')):
                src = urljoin(self.base_url, src)
            
            images.append({
                'alt': img.get('alt', ''),
                'src': src,
                'page': page_number
            })
        return images
    
    def extract_paragraphs(self, soup, page_number=1):
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short paragraphs
                paragraphs.append({
                    'content': text,
                    'page': page_number
                })
        return paragraphs
    
    def extract_headings(self, soup, page_number=1):
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({
                        'level': f'H{i}',
                        'text': text,
                        'page': page_number
                    })
        return headings
    
    def scrape_with_pagination(self, max_pages=0, page_delay=1, enable_pagination=True):
        """Scrape multiple pages with pagination support"""
        all_data = {
            'links': [],
            'images': [],
            'paragraphs': [],
            'headings': [],
            'all_pages': [],
            'total_pages': 0,
            'base_url': self.base_url,
            'start_url': self.url,
            'total_time': 0,
            'scrape_type': 'all'
        }
        
        start_time = time.time()
        current_url = self.url
        current_page = 1
        visited_urls = set()
        
        while current_url and current_url not in visited_urls:
            try:
                print(f"Scraping page {current_page}: {current_url}")
                
                # Fetch the page
                html_content, final_url = self.fetch_page(current_url)
                soup = self.parse_html(html_content)
                
                # Add page info
                all_data['all_pages'].append({
                    'page_number': current_page,
                    'url': current_url,
                    'status': 'success'
                })
                
                # Extract data from current page
                all_data['links'].extend(self.extract_links(soup, current_page))
                all_data['images'].extend(self.extract_images(soup, current_page))
                all_data['paragraphs'].extend(self.extract_paragraphs(soup, current_page))
                all_data['headings'].extend(self.extract_headings(soup, current_page))
                
                # Mark URL as visited
                visited_urls.add(current_url)
                
                # Stop if we've reached max pages
                if max_pages > 0 and current_page >= max_pages:
                    break
                
                # Find next page if pagination is enabled
                next_url = None
                if enable_pagination:
                    pagination_links = self.detect_pagination(soup)
                    
                    # Find next page link
                    for link in pagination_links:
                        link_url = link['url']
                        link_text = link['text'].lower()
                        
                        # Check if this is a "next" link
                        if any(keyword in link_text for keyword in ['next', '>', '»', 'older']):
                            if link_url not in visited_urls:
                                next_url = link_url
                                break
                    
                    # If no next link found, try to find page numbers
                    if not next_url:
                        for link in pagination_links:
                            link_url = link['url']
                            page_num = self.extract_page_number(link_url)
                            
                            if page_num == current_page + 1 and link_url not in visited_urls:
                                next_url = link_url
                                break
                
                current_url = next_url
                current_page += 1
                
                # Add delay between pages to be respectful
                if current_url and page_delay > 0:
                    time.sleep(page_delay)
                    
            except Exception as e:
                print(f"Error scraping page {current_page}: {str(e)}")
                all_data['all_pages'].append({
                    'page_number': current_page,
                    'url': current_url,
                    'status': f'error: {str(e)}'
                })
                break
        
        # Calculate total time
        all_data['total_time'] = time.time() - start_time
        all_data['total_pages'] = len(all_data['all_pages'])
        all_data['timestamp'] = datetime.now().isoformat()
        
        if all_data['all_pages']:
            all_data['last_page_url'] = all_data['all_pages'][-1]['url']
        
        return all_data
    
    def scrape_single_page(self):
        """Scrape only a single page"""
        html_content, _ = self.fetch_page()
        soup = self.parse_html(html_content)
        
        return {
            'links': self.extract_links(soup),
            'images': self.extract_images(soup),
            'paragraphs': self.extract_paragraphs(soup),
            'headings': self.extract_headings(soup),
            'all_pages': [{'page_number': 1, 'url': self.url, 'status': 'success'}],
            'total_pages': 1,
            'base_url': self.base_url,
            'start_url': self.url,
            'total_time': 0,
            'timestamp': datetime.now().isoformat(),
            'last_page_url': self.url,
            'scrape_type': 'all'
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        url = data.get('url')
        max_pages = data.get('maxPages', 0)
        page_delay = data.get('pageDelay', 1)
        enable_pagination = data.get('enablePagination', True)
        scrape_type = data.get('scrapeType', 'all')
        
        if not url:
            return jsonify({'error': 'URL tidak boleh kosong'}), 400
        
        scraper = WebScraper(url)
        
        # Scrape with or without pagination
        if enable_pagination and max_pages != 1:
            results = scraper.scrape_with_pagination(
                max_pages=max_pages,
                page_delay=page_delay,
                enable_pagination=enable_pagination
            )
        else:
            results = scraper.scrape_single_page()
        
        # Add scrape type to results
        results['scrape_type'] = scrape_type
        
        # Filter by scrape type if needed
        if scrape_type != 'all':
            filter_results_by_type(results, scrape_type)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def filter_results_by_type(results, scrape_type):
    """Filter results based on scrape type"""
    if scrape_type == 'links':
        # Keep only links, remove others
        results['images'] = []
        results['paragraphs'] = []
        results['headings'] = []
    elif scrape_type == 'images':
        results['links'] = []
        results['paragraphs'] = []
        results['headings'] = []
    elif scrape_type == 'text':
        results['links'] = []
        results['images'] = []
        results['headings'] = []
    elif scrape_type == 'headings':
        results['links'] = []
        results['images'] = []
        results['paragraphs'] = []

# Add new routes for direct downloads
@app.route('/download/<data_type>', methods=['GET'])
def download_data(data_type):
    """Direct download endpoint for different data types"""
    try:
        # Get parameters from request
        url = request.args.get('url')
        scrape_type = request.args.get('type', 'all')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        scraper = WebScraper(url)
        results = scraper.scrape_single_page()
        
        # Filter based on type
        if scrape_type != 'all':
            filter_results_by_type(results, scrape_type)
        
        # Generate CSV based on data_type
        output = io.StringIO()
        writer = csv.writer(output)
        
        if data_type == 'links':
            writer.writerow(['Text', 'URL', 'Page'])
            for link in results.get('links', []):
                writer.writerow([link.get('text', ''), link.get('url', ''), link.get('page', 1)])
            filename = 'links.csv'
            
        elif data_type == 'images':
            writer.writerow(['Alt Text', 'Source URL', 'Page'])
            for img in results.get('images', []):
                writer.writerow([img.get('alt', ''), img.get('src', ''), img.get('page', 1)])
            filename = 'images.csv'
            
        elif data_type == 'headings':
            writer.writerow(['Level', 'Text', 'Page'])
            for heading in results.get('headings', []):
                writer.writerow([heading.get('level', ''), heading.get('text', ''), heading.get('page', 1)])
            filename = 'headings.csv'
            
        elif data_type == 'text':
            writer.writerow(['Content', 'Page'])
            for paragraph in results.get('paragraphs', []):
                writer.writerow([paragraph.get('content', ''), paragraph.get('page', 1)])
            filename = 'text.csv'
            
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("=" * 60)
    print("🚀 Web Scraper with Pagination Started!")
    print("=" * 60)
    print("📍 Buka browser dan akses: http://127.0.0.1:5000")
    print("📄 Fitur Pagination: Auto-detect next page links")
    print("📥 Download Options: Pilih jenis data untuk CSV")
    print("⏱️  Delay antar halaman: Konfigurasi di UI")
    print("⛔ Tekan CTRL+C untuk berhenti")
    print("=" * 60)
    app.run(debug=True, port=5000)