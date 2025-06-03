import streamlit as st
import pandas as pd
import uuid

# Initialize session state
if "recipes" not in st.session_state:
    st.session_state.recipes = []
if "instruction_steps" not in st.session_state:
    st.session_state.instruction_steps = [""]

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

# Search with filters
st.subheader("🔍 Search Recipes")

# Dropdown filters
cuisine_filter = st.selectbox("Filter by Cuisine", ["All", "Indian", "Italian", "Mexican", "Chinese", "Other"])
tag_filter = st.selectbox("Filter by Tag", ["All", "Vegetarian", "Non-Vegetarian", "Vegan", "Other"])
status_filter = st.selectbox("Filter by Status", ["All", "To Try", "Favorite", "Made Before"])
search_query = st.text_input("Search by Recipe Name")

# Apply filters
filtered_recipes = st.session_state.recipes

if cuisine_filter != "All":
    filtered_recipes = [r for r in filtered_recipes if r["cuisine_type"] == cuisine_filter]

if tag_filter != "All":
    filtered_recipes = [r for r in filtered_recipes if r["tag"] == tag_filter]

if status_filter != "All":
    filtered_recipes = [r for r in filtered_recipes if r.get("status", "") == status_filter]

if search_query.strip():
    filtered_recipes = [
        r for r in filtered_recipes
        if search_query.lower() in r["name"].lower()
    ]

# Display recipes
display_recipes(filtered_recipes)
