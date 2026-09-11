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

SRILA_PRABHUPADA_BIO_MD = """
**His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda** (1896&ndash;1977) was the founder-ācārya of the International Society for Krishna Consciousness (ISKCON). Born in Calcutta, he was instructed by his own spiritual master, **Śrīla Bhaktisiddhānta Sarasvatī Ṭhākura**, to carry the teachings of Kṛṣṇa consciousness to the English-speaking world.

In 1965, at the age of 69, he traveled alone to New York City with little more than a trunk of translated books and unwavering faith in his spiritual master's order. Within little more than a decade, he had founded over a hundred temples and farm communities across six continents, initiated thousands of disciples, and translated and wrote commentary on the core scriptures of the Gauḍīya Vaiṣṇava tradition&mdash;including **Bhagavad-gītā As It Is** and the multi-volume **Śrīmad-Bhāgavatam**&mdash;works now read in dozens of languages worldwide.

Śrīla Prabhupāda is remembered by his followers not merely as an institution-builder but as the living embodiment of the disciplic succession he served: a spiritual master who asked nothing for himself and gave everything so that others could find shelter at the feet of Kṛṣṇa. He left this world in Vṛndāvana in 1977, and his instructions&mdash;preserved in his books, letters, and recorded classes&mdash;remain the foundation on which this book, and the entire mission it serves, stands.
"""

BHAKTI_TIRTHA_SWAMI_BIO_MD = """
**His Holiness Bhakti Tīrtha Swami (Kṛṣṇapāda)** (1950&ndash;2005) was among the first African-American sannyāsīs and initiating gurus within ISKCON. Initiated by Śrīla Prabhupāda, he went on to become a tireless missionary, scholar, and community-builder whose life is remembered as a model of fearless, sacrificial service.

He led some of ISKCON's most demanding missionary work across West Africa&mdash;including Nigeria, Ghana, the Ivory Coast, Liberia, and Zimbabwe&mdash;helping establish self-sufficient farming communities, clinics, schools, and cottage industries at a time when few were willing to take on such physical hardship for the sake of preaching. He also preached behind the Iron Curtain during the Communist era, enduring imprisonment and state surveillance rather than abandon his mission.

Holding a doctorate and serving for years on ISKCON's Governing Body Commission (GBC), Bhakti Tīrtha Swami authored several books, including his well-known **Spiritual Warrior** series, applying Kṛṣṇa conscious principles to the everyday struggles of the heart. Those who knew him describe a spiritual father of unusual sensitivity&mdash;someone who carried the anxieties of his disciples as his own. He passed away in 2005 after a long battle with cancer, a "spiritual warrior" to the end, and his example of uncompromised purity and selfless devotee care is the guiding spirit behind this book.
"""

def all_pages_html():
    return (
        _section("Author Biography", AUTHOR_BIO_MD)
        + '<div class="fm-page-break"></div>'
        + _section("Śrīla Prabhupāda", SRILA_PRABHUPADA_BIO_MD)
        + '<div class="fm-page-break"></div>'
        + _section("His Holiness Bhakti Tīrtha Swami", BHAKTI_TIRTHA_SWAMI_BIO_MD)
        + '<div class="fm-page-break"></div>'
        + _section("In Memoriam: The Caring Father", IN_MEMORIAM_MD)
    )
