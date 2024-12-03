import streamlit as st

def process_vcf(file_content: str) -> str:
    """
    Traite le contenu d'un fichier .vcf pour appliquer les règles suivantes :
    - Remplace les numéros commençant par 00229, 229, ou +229 par +22901.
    - Ajoute le préfixe 01 aux numéros locaux commençant par un chiffre compris entre 40 et 99.

    Args:
        file_content (str): Contenu du fichier .vcf.

    Returns:
        str: Contenu du fichier .vcf modifié.
    """
    lines = file_content.splitlines()
    updated_lines = []
    current_vcard = []

    for line in lines:
        if line.startswith("BEGIN:VCARD"):
            current_vcard = [line]
        elif line.startswith("END:VCARD"):
            current_vcard.append(line)
            # Traiter les numéros de téléphone dans la vCard
            current_vcard = process_phone_numbers_in_vcard(current_vcard)
            updated_lines.extend(current_vcard)
        else:
            current_vcard.append(line)

    return "\n".join(updated_lines)

def process_phone_numbers_in_vcard(vcard_lines):
    """
    Traite les numéros de téléphone dans une carte de visite.

    Args:
        vcard_lines (list): Liste des lignes d'une carte de visite.

    Returns:
        list: Liste modifiée des lignes d'une carte de visite.
    """
    updated_vcard = []
    for line in vcard_lines:
        if line.startswith("TEL") or line.startswith("item") or  line.startswith("FN"):
            tel_line = line.split(":")[1].strip()
            tel_line_no_space = tel_line.replace(" ", "")

            # Cas 1 : Remplacer les préfixes 00229, 229, ou +229 par +22901
            if tel_line_no_space.startswith("00229"):
                updated_tel = "+22901" + tel_line_no_space[5:]
            elif tel_line_no_space.startswith("229"):
                updated_tel = "+22901" + tel_line_no_space[3:]
            elif tel_line_no_space.startswith("+229"):
                updated_tel = "+22901" + tel_line_no_space[4:]

            # Cas 2 : Ajouter un préfixe 01 pour les numéros locaux (40-99)
            elif tel_line_no_space[:2].isdigit() and 40 <= int(tel_line_no_space[:2]) <= 99:
                updated_tel = "01" + tel_line_no_space

            # Sinon, laisser le numéro tel quel
            else:
                updated_tel = tel_line_no_space

            # Mettre à jour la ligne avec le numéro traité
            updated_line = line.replace(tel_line, updated_tel)
            updated_vcard.append(updated_line)
        else:
            updated_vcard.append(line)

    return updated_vcard


# Interface utilisateur avec Streamlit
st.title("Mise à jour des numéros de téléphone dans un fichier .vcf")

st.write(
    """
    Cette application traite les numéros de téléphone dans un fichier `.vcf` en appliquant les règles suivantes :
    - Remplace les préfixes `00229`, `229`, ou `+229` par `+22901`.
    - Ajoute le préfixe `01` aux numéros locaux commençant par un chiffre entre `40` et `99`.
    - Laisse les autres numéros inchangés.
    """
)

uploaded_file = st.file_uploader("Téléchargez un fichier .vcf", type=["vcf"])

if uploaded_file:
    try:
        # Lire le contenu du fichier téléchargé
        file_content = uploaded_file.read().decode("utf-8")
        
        # Traiter le fichier
        updated_content = process_vcf(file_content)
        
        # Permettre le téléchargement du fichier modifié
        st.success("Le fichier a été traité avec succès.")
        st.download_button(
            label="Télécharger le fichier corrigé",
            data=updated_content,
            file_name="processed_" + uploaded_file.name,
            mime="text/x-vcard"
        )
    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement du fichier : {e}")
