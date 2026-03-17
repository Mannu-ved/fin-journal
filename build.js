#!/usr/bin/env node
/**
 * Simple build script to generate blog post HTML pages from markdown files.
 * Run: node build.js
 */

const fs = require('fs');
const path = require('path');

const POSTS_DIR = path.join(__dirname, 'content', 'posts');
const BLOG_DIR = path.join(__dirname, 'blog');
const TEMPLATE_PATH = path.join(BLOG_DIR, 'post-template.html');

// Simple markdown to HTML converter
function mdToHtml(md) {
  let html = md;

  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Bold and italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Blockquotes
  html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');

  // Unordered lists
  html = html.replace(/^[\-\*] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>\n${match}</ul>\n`);

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2">$1</a>');

  // Paragraphs - wrap standalone lines
  const lines = html.split('\n');
  const result = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line === '') {
      result.push('');
    } else if (
      line.startsWith('<h') ||
      line.startsWith('<ul') ||
      line.startsWith('</ul') ||
      line.startsWith('<ol') ||
      line.startsWith('</ol') ||
      line.startsWith('<li') ||
      line.startsWith('<blockquote') ||
      line.startsWith('<table') ||
      line.startsWith('<tr') ||
      line.startsWith('<td') ||
      line.startsWith('<th') ||
      line.startsWith('</table') ||
      line.startsWith('</tr') ||
      line.startsWith('<hr')
    ) {
      result.push(line);
    } else if (line.length > 0) {
      result.push(`<p>${line}</p>`);
    }
  }

  return result.join('\n');
}

// Parse frontmatter from markdown
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { meta: {}, body: content };

  const meta = {};
  match[1].split('\n').forEach(line => {
    const [key, ...valueParts] = line.split(':');
    if (key && valueParts.length) {
      meta[key.trim()] = valueParts.join(':').trim().replace(/^["']|["']$/g, '');
    }
  });

  return { meta, body: match[2].trim() };
}

// Format date
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

// Main build
function build() {
  if (!fs.existsSync(POSTS_DIR)) {
    console.log('No content/posts directory found. Create markdown posts there first.');
    return;
  }

  const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
  const files = fs.readdirSync(POSTS_DIR).filter(f => f.endsWith('.md'));

  console.log(`Building ${files.length} blog posts...`);

  files.forEach(file => {
    const content = fs.readFileSync(path.join(POSTS_DIR, file), 'utf8');
    const { meta, body } = parseFrontmatter(content);
    const htmlContent = mdToHtml(body);
    const slug = file.replace('.md', '');

    let page = template
      .replace(/\{\{TITLE\}\}/g, meta.title || slug)
      .replace(/\{\{CATEGORY\}\}/g, meta.category || 'General')
      .replace(/\{\{DATE\}\}/g, meta.date ? formatDate(meta.date) : '')
      .replace(/\{\{EXCERPT\}\}/g, (meta.title || slug) + ' - My Finance Journal')
      .replace('{{CONTENT}}', htmlContent);

    const outPath = path.join(BLOG_DIR, `${slug}.html`);
    fs.writeFileSync(outPath, page);
    console.log(`  ✓ ${slug}.html`);
  });

  console.log('Build complete!');
}

build();
