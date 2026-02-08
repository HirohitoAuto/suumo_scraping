# GitHub Copilot Instructions

## Context Exclusions

To save tokens and improve performance, the following directories should be excluded from GitHub Copilot's context:

- `scraping/data/` - This directory contains scraped data (CSV files and other data files) that are not needed for code suggestions.

## Project Overview

This is a SUUMO web scraping project that collects real estate property information. The scraped data is stored in the `scraping/data/` directory but does not need to be analyzed by Copilot for code completion.
