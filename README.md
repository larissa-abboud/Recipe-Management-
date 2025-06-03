# Recipe Management System with AI Recipe Generator

This is a Streamlit app to manage your recipes with features like adding, editing, deleting recipes, tagging them with status (Favorite, To Try, Made Before), and an AI-powered recipe generator using OpenAI GPT models.

---

## Features

- Add, edit, delete recipes with detailed instructions.
- Tag recipes by type (Vegetarian, Vegan, etc.) and status (Favorite, To Try, Made Before).
- Search recipes by name, cuisine, tag, or status.
- Generate new recipes automatically by entering a recipe name, powered by OpenAI GPT.

---

## Requirements

- Python 3.7+
- `streamlit`
- `openai`
- `pandas`

---

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt


2. Set your OpenAI API key Using environment variables

   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"

3. Set your OpenAI API key Using Streamlit Secrets

   ```bash
   OPENAI_API_KEY="your_openai_api_key_here"

## Usage


   ```bash
streamlit run app.py