import streamlit as st
import pandas as pd
import uuid
import random

# Initialize session state
if "recipes" not in st.session_state:
    st.session_state.recipes = []
if "instruction_steps" not in st.session_state:
    st.session_state.instruction_steps = [""]

# Mock AI recipe generator function
def ai_generate_recipe(name):
    # Simple mock data for demo purposes
    cuisines = ["Indian", "Italian", "Mexican", "Chinese", "Other"]
    tags = ["Vegetarian", "Non-Vegetarian", "Vegan", "Other"]
    statuses = ["To Try", "Favorite", "Made Before"]
    
    ingredients = [
        "1 cup of ingredient A",
        "2 tablespoons of ingredient B",
        "3 slices of ingredient C",
        "Salt to taste",
        "1 teaspoon of spice D"
    ]
    
    instructions = [
        "Mix all ingredients.",
        "Cook on medium heat for 15 minutes.",
        "Let it cool for 5 minutes.",
        "Serve and enjoy!"
    ]
    
    recipe = {
        "id": str(uuid.uuid4()),
        "name": name,
        "ingredients": ", ".join(random.sample(ingredients, k=3)),
        "cuisine_type": random.choice(cuisines),
        "prep_time": random.randint(10, 60),
        "instructions": instructions,
        "tag": random.choice(tags),
        "status": random.choice(statuses)
    }
    return recipe

# Helper: Display all recipes
def display_recipes(filtered):
    if not filtered:
        st.info("No recipes found.")
        return

    for idx, recipe in enumerate(filtered):
        with st.expander(f"{recipe['name']} ({recipe['cuisine_type']})"):
            st.write(f"**Ingredients:** {recipe['ingredients']}")
            st.markdown("**Instructions:**")
            for step in recipe["instructions"]:
                st.markdown(f"- {step}")
            st.write(f"**Preparation Time:** {recipe['prep_time']} mins")
            st.write(f"**Tag:** {recipe['tag']}")
            st.write(f"**Status:** {recipe.get('status', 'Not Set')}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Edit", key=f"edit_{recipe['id']}"):
                    edit_recipe(recipe['id'])
            with col2:
                if st.button("Delete", key=f"delete_{recipe['id']}"):
                    st.session_state.recipes = [r for r in st.session_state.recipes if r["id"] != recipe["id"]]
                    st.success("Recipe deleted.")
                    st.rerun()

# Helper: Edit recipe
def edit_recipe(recipe_id):
    recipe = next(r for r in st.session_state.recipes if r["id"] == recipe_id)
    st.session_state.editing = recipe_id
    editing_steps = recipe["instructions"][:]

    with st.form("edit_form"):
        name = st.text_input("Recipe Name", value=recipe["name"])
        ingredients = st.text_area("Ingredients", value=recipe["ingredients"])
        cuisine_type = st.selectbox(
            "Cuisine Type",
            ["Indian", "Italian", "Mexican", "Chinese", "Other"],
            index=["Indian", "Italian", "Mexican", "Chinese", "Other"].index(recipe["cuisine_type"])
        )
        prep_time = st.number_input("Preparation Time (mins)", min_value=1, value=recipe["prep_time"])
        tag = st.selectbox(
            "Tag",
            ["Vegetarian", "Non-Vegetarian", "Vegan", "Other"],
            index=["Vegetarian", "Non-Vegetarian", "Vegan", "Other"].index(recipe["tag"])
        )
        status = st.selectbox(
            "Status",
            ["To Try", "Favorite", "Made Before"],
            index=["To Try", "Favorite", "Made Before"].index(recipe.get("status", "To Try"))
        )

        st.markdown("**Edit Instructions:**")
        new_steps = []
        for i, step in enumerate(editing_steps):
            step_text = st.text_input(f"Step {i+1}", value=step, key=f"edit_step_{i}")
            new_steps.append(step_text)

        if st.form_submit_button("Add Instruction Step"):
            new_steps.append("")
            st.rerun()

        submitted = st.form_submit_button("Update Recipe")
        if submitted:
            recipe.update({
                "name": name,
                "ingredients": ingredients,
                "cuisine_type": cuisine_type,
                "prep_time": prep_time,
                "instructions": new_steps,
                "tag": tag,
                "status": status
            })
            st.success("Recipe updated.")
            st.session_state.editing = None
            st.rerun()

# === AI Recipe Generator Section ===
st.title("🤖 AI Recipe Generator")
ai_recipe_name = st.text_input("Enter recipe name to generate")
if st.button("Generate Recipe"):
    if not ai_recipe_name.strip():
        st.error("Please enter a recipe name.")
    else:
        generated_recipe = ai_generate_recipe(ai_recipe_name.strip())
        st.session_state.recipes.append(generated_recipe)
        st.success(f"Recipe '{ai_recipe_name}' generated and added!")
        st.rerun()

st.divider()

# App Title
st.title("📖 Recipe Management System")

# Add New Recipe
with st.form("add_recipe"):
    st.subheader("➕ Add New Recipe")
    name = st.text_input("Recipe Name")
    ingredients = st.text_area("Ingredients (comma separated)")
    cuisine_type = st.selectbox("Cuisine Type", ["Indian", "Italian", "Mexican", "Chinese", "Other"])
    prep_time = st.number_input("Preparation Time (mins)", min_value=1)
    tag = st.selectbox("Tag", ["Vegetarian", "Non-Vegetarian", "Vegan", "Other"])
    status = st.selectbox("Status", ["To Try", "Favorite", "Made Before"])

    st.markdown("**Instructions:**")
    for i, step in enumerate(st.session_state.instruction_steps):
        st.session_state.instruction_steps[i] = st.text_input(f"Step {i+1}", value=step, key=f"instr_{i}")

    if st.form_submit_button("Add Instruction Step"):
        st.session_state.instruction_steps.append("")
        st.rerun()

    submit = st.form_submit_button("Add Recipe")
    if submit:
        new_recipe = {
            "id": str(uuid.uuid4()),
            "name": name,
            "ingredients": ingredients,
            "cuisine_type": cuisine_type,
            "prep_time": prep_time,
            "instructions": [step for step in st.session_state.instruction_steps if step.strip() != ""],
            "tag": tag,
            "status": status
        }
        st.session_state.recipes.append(new_recipe)
        st.session_state.instruction_steps = [""]
        st.success("Recipe added!")
        st.rerun()

st.divider()

# Search
st.subheader("🔍 Search Recipes")
search_query = st.text_input("Search by name, cuisine, tag, or status")
filtered_recipes = [
    r for r in st.session_state.recipes
    if search_query.lower() in r["name"].lower()
    or search_query.lower() in r["cuisine_type"].lower()
    or search_query.lower() in r["tag"].lower()
    or search_query.lower() in r.get("status", "").lower()
]

# Display recipes
display_recipes(filtered_recipes)
