from flask import Flask, render_template, request, jsonify, make_response
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),  # Default to localhost
        user=os.getenv('DB_USER', 'root'),       # Default to root
        password=os.getenv('DB_PASSWORD', ''),   # Default to empty password
        database=os.getenv('DB_NAME', 'endometrial_cancer_database')  # Default database name
    )
    return connection

# Home Page Route
@app.route("/")
def home():
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Retrieve dark mode state from cookies
    return render_template("home.html", dark_mode=dark_mode)

# Toggle Dark Mode Route
@app.route("/toggle-dark-mode")
def toggle_dark_mode():
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Get current dark mode state
    new_mode = 'enabled' if dark_mode == 'disabled' else 'disabled'  # Toggle the state
    response = make_response("Dark mode toggled")
    response.set_cookie('dark-mode', new_mode)  # Set the new state in cookies
    return response

# Search Route
@app.route("/search", methods=["GET"])
def search():
    database = request.args.get("database")
    query = request.args.get("query")
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Pass dark mode state to template

    if database == "gene":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ensembl_gene_id, gene_abbr, gene_name, description
            FROM gene_data 
            WHERE gene_name LIKE %s OR gene_abbr LIKE %s OR ensembl_gene_id LIKE %s
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
        gene_results = cursor.fetchall()

        transcript_results = []
        for gene in gene_results:
            cursor.execute("""
                SELECT transcript_id
                FROM transcript_data
                WHERE ensembl_gene_id = %s
            """, (gene['ensembl_gene_id'],))
            transcripts = cursor.fetchall()
            transcript_results.append({
                'ensembl_gene_id': gene['ensembl_gene_id'],
                'transcripts': [t['transcript_id'] for t in transcripts]
            })

        cursor.close()
        conn.close()

        result_count = len(gene_results)
        transcript_count = sum(len(t['transcripts']) for t in transcript_results)

        if result_count == 0:
            message = "No genes found matching the search query."
        else:
            message = f"Found {result_count} gene(s) matching your search query and {transcript_count} transcript(s) associated."

        return render_template(
            "gene.html", 
            query=query, 
            gene_results=gene_results, 
            transcript_results=transcript_results, 
            message=message,
            dark_mode=dark_mode
        )
    elif database == "transcript":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.transcript_id, 
                t.ensembl_gene_id, 
                t.protein_id, 
                t.biotype,
                g.gene_abbr
            FROM transcript_data t
            LEFT JOIN gene_data g ON t.ensembl_gene_id = g.ensembl_gene_id
            WHERE t.transcript_id LIKE %s 
            OR t.ensembl_gene_id LIKE %s 
            OR t.protein_id LIKE %s 
            OR g.gene_abbr LIKE %s
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
        transcript_results = cursor.fetchall()

        cursor.close()
        conn.close()

        result_count = len(transcript_results)

        if result_count == 0:
            message = "No transcripts found matching the search query."
        else:
            message = f"Found {result_count} transcript(s) matching your search query."

        return render_template(
            "transcript.html",
            query=query,
            transcript_results=transcript_results,
            message=message,
            dark_mode=dark_mode
        )
    
    elif database == "pathway":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT element, description, pathway_def
            FROM networks
            WHERE element LIKE %s OR description LIKE %s
        """, ('%' + query + '%', '%' + query + '%'))
        pathway_results = cursor.fetchall()

        cursor.close()
        conn.close()

        result_count = len(pathway_results)

        if result_count == 0:
            message = "No pathways found matching the search query."
        else:
            message = f"Found {result_count} pathway(s) matching your search query."

        return render_template(
            "pathway.html",
            query=query,
            pathway_results=pathway_results,
            message=message,
            dark_mode=dark_mode
        )

    else:
        return render_template("error.html", message="Invalid database selection.", dark_mode=dark_mode)

@app.route("/data/search", methods=["GET"])
def search_json():
    database = request.args.get("database")
    query = request.args.get("query")

    if database == "gene":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ensembl_gene_id, gene_abbr, gene_name, description
            FROM gene_data 
            WHERE gene_name LIKE %s OR gene_abbr LIKE %s OR ensembl_gene_id LIKE %s
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
        gene_results = cursor.fetchall()

        transcript_results = []
        for gene in gene_results:
            cursor.execute("""
                SELECT transcript_id
                FROM transcript_data
                WHERE ensembl_gene_id = %s
            """, (gene['ensembl_gene_id'],))
            transcripts = cursor.fetchall()
            transcript_results.append({
                'ensembl_gene_id': gene['ensembl_gene_id'],
                'transcripts': [t['transcript_id'] for t in transcripts]
            })

        cursor.close()
        conn.close()

        return jsonify({
            "gene_results": gene_results,
            "transcript_results": transcript_results
        })
    
    elif database == "transcript":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.transcript_id, 
                t.ensembl_gene_id, 
                t.protein_id, 
                t.biotype,
                g.gene_abbr
            FROM transcript_data t
            LEFT JOIN gene_data g ON t.ensembl_gene_id = g.ensembl_gene_id
            WHERE t.transcript_id LIKE %s 
            OR t.ensembl_gene_id LIKE %s 
            OR t.protein_id LIKE %s 
            OR g.gene_abbr LIKE %s
        """, ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
        transcript_results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"transcript_results": transcript_results})
    
    elif database == "pathway":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT element, description, pathway_def
            FROM networks
            WHERE element LIKE %s OR description LIKE %s
        """, ('%' + query + '%', '%' + query + '%'))
        pathway_results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"pathway_results": pathway_results})

    else:
        return jsonify({"error": "Invalid database selection."}), 400

@app.route("/gene-overview")
def gene_overview():
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Pass dark mode state to template
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT gene_abbr, gene_name, ko_info, ensembl_gene_id
            FROM gene_data
            ORDER BY gene_abbr ASC
        """)
        gene_data = cursor.fetchall()

        column_mapping = {
            "gene_abbr": "Gene Symbol",
            "gene_name": "Gene Name",
            "ko_info": "KO",
            "ensembl_gene_id": "Ensembl Gene ID"
        }

        column_names = [column_mapping[col] for col in gene_data[0].keys()] if gene_data else []

        cursor.close()
        conn.close()

        return render_template(
            "gene_overview.html", 
            gene_data=gene_data, 
            column_names=column_names, 
            dark_mode=dark_mode
        )
    except Exception as e:
        return render_template(
            "error.html", 
            message=f"An error occurred: {str(e)}", 
            dark_mode=dark_mode
        )
@app.route("/data/gene-overview", methods=["GET"])
def gene_overview_json():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT gene_abbr, gene_name, ko_info, ensembl_gene_id
            FROM gene_data
            ORDER BY gene_abbr ASC
        """)
        gene_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(gene_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/transcript-overview")
def transcript_overview():
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Pass dark mode state to template
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT 
                t.ensembl_gene_id, 
                g.gene_abbr AS gene_abbr, 
                t.transcript_id, 
                t.protein_id, 
                t.biotype
            FROM transcript_data t
            LEFT JOIN gene_data g ON t.ensembl_gene_id = g.ensembl_gene_id
            ORDER BY g.gene_abbr ASC
        """)
        transcript_data = cursor.fetchall()

        cursor.execute("""
            SELECT biotype, COUNT(*) AS count 
            FROM transcript_data 
            GROUP BY biotype
        """)
        biotype_data = cursor.fetchall()

        total_transcripts = sum(b['count'] for b in biotype_data)
        biotype_distribution = [
            {"biotype": b["biotype"], "percentage": round((b["count"] / total_transcripts) * 100, 2)} 
            for b in biotype_data
        ]

        column_mapping = {
            "gene_abbr": "Gene Symbol",
            "ensembl_gene_id": "Ensembl Gene ID",
            "transcript_id": "Ensembl Transcript ID",
            "protein_id": "Ensembl Protein ID",
            "biotype": "Biotype"
        }

        column_names = [column_mapping[col] for col in transcript_data[0].keys()] if transcript_data else []

        cursor.close()
        conn.close()

        return render_template(
            "transcript_overview.html",
            transcript_data=transcript_data,
            column_names=column_names,
            biotype_distribution=biotype_distribution,
            dark_mode=dark_mode
        )
    except Exception as e:
        return render_template(
            "error.html", 
            message=f"An error occurred: {str(e)}", 
            dark_mode=dark_mode
        )
@app.route("/data/transcript-overview", methods=["GET"])
def transcript_overview_json():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT 
                t.ensembl_gene_id, 
                g.gene_abbr AS gene_abbr, 
                t.transcript_id, 
                t.protein_id, 
                t.biotype
            FROM transcript_data t
            LEFT JOIN gene_data g ON t.ensembl_gene_id = g.ensembl_gene_id
            ORDER BY g.gene_abbr ASC
        """)
        transcript_data = cursor.fetchall()

        cursor.execute("""
            SELECT biotype, COUNT(*) AS count 
            FROM transcript_data 
            GROUP BY biotype
        """)
        biotype_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "transcript_data": transcript_data,
            "biotype_distribution": biotype_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/pathway-overview")
def pathway_overview():
    dark_mode = request.cookies.get('dark-mode', 'disabled')  # Pass dark mode state to template
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT element, description, pathway_def
            FROM networks
            ORDER BY element ASC
        """)
        pathway_data = cursor.fetchall()

        column_mapping = {
            "element": "KEGG Element",
            "description": "Description",
            "pathway_def": "Pathway Definition"
        }

        column_names = [column_mapping[col] for col in pathway_data[0].keys()] if pathway_data else []

        cursor.close()
        conn.close()

        return render_template(
            "pathway_overview.html", 
            pathway_data=pathway_data, 
            column_names=column_names, 
            dark_mode=dark_mode
        )
    except Exception as e:
        return render_template(
            "error.html", 
            message=f"An error occurred: {str(e)}", 
            dark_mode=dark_mode
        )

@app.route("/data/pathway-overview", methods=["GET"])
def pathway_overview_json():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT element, description, pathway_def
            FROM networks
            ORDER BY element ASC
        """)
        pathway_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(pathway_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)