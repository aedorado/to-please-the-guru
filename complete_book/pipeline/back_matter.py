import parse_chapter
render_paragraphs = parse_chapter.render_paragraphs

def _section(label, body_md):
    return f'<div class="fm-page"><h2 class="fm-heading">{label}</h2>{render_paragraphs(body_md)}</div>'

AUTHOR_BIO_MD = """
**His Holiness Bhakti Dhīra Dāmodara Swami** is a sannyāsi and a widely traveled spiritual leader within the International Society for Krishna Consciousness (ISKCON). Born with a deep, natural spiritual inclination, he adopted full-time monastic life after coming into contact with the sublime teachings of Śrīla Prabhupāda.

Maharaj was fortunate to spend many years as a close personal servant to his beloved spiritual master, **His Holiness Bhakti Tīrtha Swami (Kṛṣṇapāda)**, from whom he received sannyāsa and his sannyāsa recommendation. Maharaj served as an active instrument in Bhakti Tīrtha Swami's pioneering, high-potency missions across West Africa&mdash;including Nigeria, Ghana, the Ivory Coast, Liberia, and Zimbabwe&mdash;assisting in the establishment of self-sufficient farming communities, clinics, schools, and cottage industries.

Known for his uncompromising, straightforward, and intensely compassionate style of preaching, Maharaj sits directly on the rug, looking his listeners in the eye, and addressing the deep struggles of their hearts. His life is entirely dedicated to protecting the disciplic succession, pushing devotees to intensify their daily morning *sādhana*, and building a practical, loving future for the next generation of Vaiṣṇavas.
"""

IN_MEMORIAM_MD = """
This book is dedicated to the glorious, eternal legacy of **His Holiness Bhakti Tīrtha Swami (Kṛṣṇapāda)**, a spiritual warrior whose life defied all material odds. From preaching behind the Iron Curtain under Yugoslavian imprisonment and state police surveillance, to building self-sufficient communities in West Africa amidst extreme physical austerities, Gurudev modeled what it means to be a "transparent postman" of the disciplic line.

His mystical ability to read the hearts of his disciples, his strict prohibition of corporate transactions in favor of absolute devotee care and spiritual security, and his final, sweet phone-call blessing (*&ldquo;Don't come, stay there&hellip; people will see me in you&rdquo;*) remain the beating heart of this book.
"""

def all_pages_html():
    return (
        _section("Author Biography", AUTHOR_BIO_MD)
        + '<div class="fm-page-break"></div>'
        + _section("In Memoriam: The Caring Father", IN_MEMORIAM_MD)
    )
