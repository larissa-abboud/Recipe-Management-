import streamlit as st
import uuid
import openai

# Set your OpenAI API key here or better use Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "YOUR_API_KEY_HERE"
openai.api_key = st.secrets["OPENAI_API_KEY"]
# Initialize session state
if "recipes" not in st.session_state:
    st.session_state.recipes = []
if "instruction_steps" not in st.session_state:
    st.session_state.instruction_steps = [""]

def call_openai_to_generate_recipe(recipe_name):
    prompt = f"""
    Generate a detailed recipe for "{recipe_name}". 
    Include these fields in JSON format:

    {{
        "name": "{recipe_name}",
        "ingredients": ["list of ingredients"],
        "cuisine_type": "cuisine type",
        "prep_time": preparation time in minutes (integer),
        "instructions": ["step by step instructions"],
        "tag": "Vegetarian", "Non-Vegetarian", "Vegan" or "Other",
        "status": "To Try", "Favorite" or "Made Before"
    }}

    Make sure JSON is valid.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4", "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )

    text = response.choices[0].message.content.strip()
    return text


def parse_recipe_from_response(text):
    import json
    try:
        # The model returns JSON — parse it
        recipe_json = json.loads(text)
        
        # Some minor cleanups or fallback if keys missing
        return {
            "id": str(uuid.uuid4()),
            "name": recipe_json.get("name", "Unnamed Recipe"),
            "ingredients": ", ".join(recipe_json.get("ingredients", [])),
            "cuisine_type": recipe_json.get("cuisine_type", "Other"),
            "prep_time": int(recipe_json.get("prep_time", 30)),
            "instructions": recipe_json.get("instructions", []),
            "tag": recipe_json.get("tag", "Other"),
            "status": recipe_json.get("status", "To Try")
        }
    except Exception as e:
        st.error(f"Failed to parse AI response: {e}")
        return None

# Helper: Display all recipes (same as before, omitted here for brevity)
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
        with st.spinner("Generating recipe with AI..."):
            response_text = call_openai_to_generate_recipe(ai_recipe_name.strip())
            recipe = parse_recipe_from_response(response_text)
            if recipe:
                st.session_state.recipes.append(recipe)
                st.success(f"Recipe '{recipe['name']}' generated and added!")
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
