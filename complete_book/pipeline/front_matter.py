import build, parse_chapter
from render_chapter import PARTS

md_inline = parse_chapter.md_inline
render_paragraphs = parse_chapter.render_paragraphs

_ONES = ["zero","one","two","three","four","five","six","seven","eight","nine","ten",
         "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen",
         "eighteen","nineteen"]
_TENS = ["","","twenty","thirty","forty"]

def _num_word(n):
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return _TENS[tens] + ("-" + _ONES[ones] if ones else "")

TOTAL_CHAPTERS = PARTS[-1][1]  # last part's upper bound == total chapter count
TOTAL_CHAPTERS_WORD = _num_word(TOTAL_CHAPTERS)

TITLE_PAGE = """
<div class="fm-title-page">
  <div class="fm-title-eyebrow">A Spiritual Handbook</div>
  <h1 class="fm-title">To Please<br>the Guru</h1>
  <div class="fm-subtitle">Straight Talk on Surrender, Purity,<br>and the Sweet Burn of Devotion</div>
  <div class="fm-rule"></div>
  <div class="fm-author">His Holiness Bhakti Dhīra Dāmodara Swami</div>
</div>
"""

COPYRIGHT_PAGE = """
<div class="fm-copyright">
  <p><strong>To Please the Guru</strong><br><em>Straight Talk on Surrender, Purity, and the Sweet Burn of Devotion</em></p>
  <p>&copy; 2026 Bhakti Dhīra Dāmodara Swami &amp; The Editorial Disciple Council<br>All rights reserved.</p>
  <p>First Edition: August 2026<br>Published by: <strong>Vaidhi Bhakti Publications</strong></p>
  <p class="fm-small">Cataloging-in-Publication Data<br>
  Bhakti Dhīra Dāmodara Swami, 1968&ndash;<br>
  To Please the Guru: Straight Talk on Surrender, Purity, and the Sweet Burn of Devotion / Bhakti Dhīra Dāmodara Swami.<br>
  1. Gauḍīya Vaiṣṇavism&mdash;Philosophy. 2. Discipleship&mdash;Spiritual Master&mdash;Duty. 3. Sādhana&mdash;Purity&mdash;Devotional Service.</p>
  <p class="fm-small">All scriptural verses, Sanskrit transliterations, and translation quotations from the <em>Bhagavad-gītā As It Is</em> and the <em>Śrīmad-Bhāgavatam</em> are used with permission of the Bhaktivedanta Book Trust (BBT) &copy;. All rights reserved.</p>
  <p class="fm-small"><em>Printed in Holy Dham Mayapur, West Bengal, India.</em></p>
</div>
"""

DEDICATION_PAGE = """
<div class="fm-dedication">
  <p class="fm-ded-label">Dedicated to</p>
  <p class="fm-ded-name">His Divine Grace<br>A.C. Bhaktivedanta Swami Prabhupāda</p>
  <p class="fm-ded-desc">The Supreme Preceptor who carried the cooling nectar<br>of <em>kṛṣṇa-kathā</em> across the ocean</p>
  <p class="fm-ded-and">and</p>
  <p class="fm-ded-name">His Holiness Bhakti Tīrtha Swami<br>(Kṛṣṇapāda)</p>
  <p class="fm-ded-desc">The Spiritual Warrior who modeled strict accountability,<br>heroic preaching, and uncompromised devotee care</p>
  <p class="fm-ded-close">And to all sincere disciples who have laid down their false prestige<br>and placed their intellect, their anxieties, and their very life<br>at the lotus feet of Lord Janārdana.</p>
</div>
"""

def _section(label, body_md):
    paras = render_paragraphs(body_md)
    return f'<div class="fm-page"><h2 class="fm-heading">{label}</h2>{paras}</div>'

ACKNOWLEDGEMENTS_MD = """
*&ldquo;By the mercy of the spiritual master, even a dumb man can become a great orator, and even a lame man can cross mountains.&rdquo;* It is in this submissive mood of being a humble, transparent instrument that we offer our deepest gratitude to all those who have made this book a reality.

First, we offer our most humble and respectful obeisances to the Supreme Personality of Godhead, **Lord Śrī Kṛṣṇa (Janārdana)**, and **Lord Balarāma**, the original spiritual master. It is Lord Balarāma's divine path of strength that carries the heavy load of our spiritual lives and holds up our broken hearts in times of intense separation.

We express our eternal gratitude to **Śrīla Prabhupāda**, our supreme preceptor and caring father, who brought the cooling nectar of *kṛṣṇa-kathā* to a world burning in material anxiety. He showed us what it means to be a bona fide disciple, carrying the orders of his spiritual master on his head and preparing himself every single day to execute his duty.

We offer our deepest heart-centered appreciation to **His Holiness Bhakti Tīrtha Swami**, the spiritual warrior who modeled strict, daily accountability, and modeled a life of uncompromised purity and selfless devotee care. His heroic example of distributing books under dangerous communist regimes and Yugoslavian imprisonment, and his final phone-call blessing, are the raw fuel that ignites every page of this book.

Our deepest, most affectionate gratitude is offered to **His Holiness Bhakti Dhīra Dāmodara Swami**, whose raw, spoken *kathā* and realizations were captured and preserved here. These discourses were not spoken from a pedestal of academic detachment, but directly from the floor, sat on the rug, looking into the eyes of his listeners with the uncompromised sensitivity of a loving father.

Finally, we express our profound appreciation to the **transcription team, editorial devotees, and proofreaders** who spent countless hours listening to raw audio files, cleaning up ASR speech-recognition distortions, and carefully indexing citations. They have worked tirelessly as caretaker sweepers of the temple of the spoken word, ensuring that the unalloyed, spontaneous flavor of the original spoken lectures remains completely preserved for generations of seekers to come.
"""

PREFACE_MD = """
This book is not a dry academic thesis, nor is it a polished collection of theoretical essays. It is a compilation of transcribed heart-to-heart spiritual discourses spoken by His Holiness Bhakti Dhīra Dāmodara Swami directly to gatherings of devotees. From the bustling centers of Bengaluru and Hyderabad to SNGM and ISKCON Hosur, these words were spoken to challenge our comfortable pretenses, to smash our false egos, and to call us back to our active duties in spiritual life.

Throughout these pages, you will hear the direct, personal voice of Srila Gurudeva. As a dedicated disciple of His Holiness Bhakti Tīrtha Swami and a faithful follower of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda, Maharaj carries their standard and teachings into every chapter. He does not compromise the truth to keep his audience comfortable.

Instead, his focus is entirely on surrender, purity, and the active sacrifices we must make to protect our consciousness and build a real, devotee-centered future. This is a handbook for those who are ready to put their heads on the ground in genuine surrender.
"""

def _intro_html():
    lo1, hi1, _, _ = PARTS[0]
    lo2, hi2, _, _ = PARTS[1]
    lo3, hi3, _, _ = PARTS[2]
    return f"""
<div class="fm-page">
<h2 class="fm-heading">Introduction: Hearing on the Rug</h2>
<p style="font-style:italic;">Editorial Note: As editors, our goal has been to preserve the atmosphere of the original rooms where these discourses were delivered. When you read these chapters, we invite you to imagine sitting on the floor of a quiet temple room, surrounded by sincere souls who have laid their doubts, struggles, and pain before the speaker. The afternoon sun is fading, the mṛdaṅga is quiet, and Srila Gurudeva is sitting directly on the rug in front of you. He is looking you in the eye. He is not speaking to a corporate audience or a passive screen; he is speaking directly to your soul.</p>

<h4>The Atmosphere of the Rug</h4>
<p>Spiritual life does not begin with theoretical speculation or corporate-style seminars. It begins when we are willing to put aside our false prestige, our academic degrees, and our busy, prestigious management, and sit down humbly on the rug. Sitting on the rug represents a conscious decision to enter the <em>madhyama-adhikārī</em> realm of straightforward, loving dealings. It means we are no longer interested in showing off our dry intellectual knowledge or playing political games; we are simply ready to hear. On the rug, the speaker is not a distant lecturer on a stage; he is a loving father who is carrying your anxieties in his own heart, ready to use the scalpel of truth to perform the cataract surgery of your ignorance.</p>

<h4>The Power of the Spoken Word (<em>Vāṇī</em>)</h4>
<p>In our modern world, we are conditioned to believe that "seeing is believing". We want to see Kṛṣṇa with our own unqualified material eyes. But the great scripture <em>Śrīmad-Bhāgavatam</em> and our great ācāryas tell us that the process of spiritual seeing begins through the ears. Sincere, submissive hearing is what connects our hearts directly to the powerhouse of divine mercy (<em>vāṇī</em>). When we hear with submissive attention, the transcendental vibration penetrates our ears, pierces through our intellectual pride, and enters straight into the heart, cleansing it of the venomous Kāliya of envy, pride, and material desires. Unlike dry, polished writing, the spoken word carries the raw, spontaneous potency of the speaker's realizations. It has the power to transform a listener from a dry, mechanical ritualist into a pure devotee who can walk across the raging, dangerous rivers of material existence.</p>

<h4>The Three Progressive Stages of the Journey</h4>
<p>This book is structured to guide the reader on an internal, progressive journey of {TOTAL_CHAPTERS_WORD} chapters, replicating the spiritual development of a sincere disciple:</p>
<ol class="content-list">
<li><strong>Part I: Putting Our Head on the Ground (The Foundation of Devotion) (Chapters {lo1}&ndash;{hi1}):</strong> This section establishes the foundational standards of our spiritual practice. We learn that human behavior begins when we bow our heads to the disciplic line. We explore the compulsory nature of initiation, the absolute necessity of vigilant sadhana, and the importance of daily planning to protect our early-morning chanting from the laziness of the mind.</li>
<li><strong>Part II: Deepening Our Connection (The Internal Battle) (Chapters {lo2}&ndash;{hi2}):</strong> Having established our foundational standards, we enter the internal battlefield. We learn to perceive Kṛṣṇa through the ears, embrace the purifying burn of pure love, and execute instructions unhesitatingly without bypassing the gatekeepers of the mission. We then study the paths of strength and separation, learning to cry with genuine appreciation like a queen, and to stand as mature, responsible representatives in the empty classroom of life once the teacher departs.</li>
<li><strong>Part III: Crushing Pride and Making Our Sacrifice (The Offering) (Chapters {lo3}&ndash;{hi3}):</strong> The final section demands that we offer our lives as a practical sacrifice. We confront the venomous Kāliya of our internal pride, prepare ourselves perfectly for the ultimate test of death, and establish clear, spiritual boundaries inside our household lives, finally making the ultimate sacrifice to "boil the milk" and build devotee-centered educational communities to protect the future of our children.</li>
</ol>

<h4>The Heart Checks and Raw Prayers</h4>
<p>Every chapter in this book closes with a practical, honest <strong>Heart Check</strong> and, where the source discourse gives one, a raw, personal <strong>Prayer</strong>. These are not academic questionnaires. They are designed to serve as a mirror for your soul. They ask you to look honestly into your own heart when the teacher is out of the room, when no one is policing you, and to ask: <em>Is my spiritual life real, or is it just a prestigious, mechanical show?</em> The personal prayers are there to help you write your raw struggles, anxieties, and submissive vows on paper, addressing the Lord and the Guru directly.</p>
</div>
"""

def all_pages_html():
    return (
        f'<div class="fm-title-wrap">{TITLE_PAGE}</div>'
        f'<div class="fm-page-break"></div><div class="fm-copyright-wrap">{COPYRIGHT_PAGE}</div>'
        f'<div class="fm-page-break"></div><div class="fm-dedication-wrap">{DEDICATION_PAGE}</div>'
        f'<div class="fm-page-break"></div>{_section("Acknowledgements", ACKNOWLEDGEMENTS_MD)}'
        f'<div class="fm-page-break"></div>{_section("Preface", PREFACE_MD)}'
        f'<div class="fm-page-break"></div>{_intro_html()}'
    )
