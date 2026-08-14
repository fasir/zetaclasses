import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<div class="row g-4 courses-grid-row">'
end_marker = '<!-- ═══ SUBJECTS WE TEACH ═══ -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Markers not found')
    exit(1)

pre_content = content[:start_idx + len(start_marker)]
cards_block = content[start_idx + len(start_marker):end_idx]
post_content = content[end_idx:]

# The cards block ends with:
#       </div>
#     </div>
#   </section>
#   
# We want to keep everything from the last </div> of the cards to the end_marker as the tail.
# Let's find the position of the first closing div of the grid container.
# Actually, the grid container is closed by:
#       </div>
#     </div>

# Let's split by "\n        <!-- "
parts = cards_block.split('\n        <!-- ')

header = parts[0] # The newline after <div class="row g-4 courses-grid-row">
raw_cards = parts[1:]

if len(raw_cards) != 6:
    print('Expected 6 cards, found', len(raw_cards))
    exit(1)

# Reconstruct the cards by prepending "\n        <!-- "
cards = ['\n        <!-- ' + c for c in raw_cards]

# The last card has the closing tags at the end. We need to separate it.
last_card = cards[-1]
# Find the start of the closing tags. Each card is wrapped in <div class="col-12 ..."> ... </div></div></div>
# The cards container closing tag is `      </div>\n    </div>\n`
tail_idx = last_card.find('\n      </div>\n    </div>')
if tail_idx != -1:
    tail = last_card[tail_idx:]
    cards[-1] = last_card[:tail_idx]
else:
    print("Could not find tail")
    # try another way
    tail_idx = last_card.rfind('\n      </div>')
    if tail_idx != -1:
        tail = last_card[tail_idx:]
        cards[-1] = last_card[:tail_idx]
    else:
        tail = ""

card_map = {}
for card in cards:
    if 'Free Subject Competency Assessment' in card:
        card_map['assessment'] = card
    elif 'CBSE Subject Tuitions' in card or 'CBSE Tuitions' in card:
        card_map['cbse'] = card
    elif 'Kerala State Board' in card:
        card_map['kerala'] = card
    elif 'NEET / JEE Coaching' in card:
        card_map['neet'] = card
    elif 'IGCSE & A-Level Subject Tuitions' in card or 'IGCSE & A-Level Tuitions' in card:
        card_map['igcse'] = card
    elif 'Board Exam Revision Camp' in card:
        card_map['revision'] = card

order = ['assessment', 'cbse', 'kerala', 'neet', 'igcse', 'revision']
new_cards = []
for key in order:
    if key not in card_map:
        print('Missing key:', key)
        exit(1)
    
    card_content = card_map[key]
    new_num = order.index(key) + 1
    card_content = re.sub(r'<!-- \d+\. ', f'<!-- {new_num}. ', card_content, count=1)
    new_cards.append(card_content)

new_cards_block = header + ''.join(new_cards) + tail
new_content = pre_content + new_cards_block + post_content

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Successfully reordered cards')
