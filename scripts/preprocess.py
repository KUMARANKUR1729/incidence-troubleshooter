# scripts/preprocess.py
import json, os
INPATH = "data/incidents.jsonl"
OUTPATH = "data/chunks.jsonl"
CHUNK_SENTENCES = 2

def simple_sentence_split(text):
    parts = [s.strip() for s in text.replace("\r"," ").split(".") if s.strip()]
    return parts

def make_chunks(text, incident_id, service, sentences_per_chunk=CHUNK_SENTENCES):
    sents = simple_sentence_split(text)
    chunks = []
    for i in range(0, len(sents), sentences_per_chunk):
        chunk_sents = sents[i:i+sentences_per_chunk]
        chunk_text = ". ".join(chunk_sents).strip()
        if chunk_text:
            chunks.append({
                "chunk_id": f"{incident_id}_{i//sentences_per_chunk}",
                "incident_id": incident_id,
                "service": service,
                "chunk_index": i//sentences_per_chunk,
                "text": chunk_text
            })
    if not chunks and text.strip():
        chunks.append({
            "chunk_id": f"{incident_id}_0",
            "incident_id": incident_id,
            "service": service,
            "chunk_index": 0,
            "text": text.strip()
        })
    return chunks

def main():
    os.makedirs(os.path.dirname(OUTPATH), exist_ok=True)
    total_chunks = 0
    with open(INPATH, "r", encoding="utf-8") as fin, open(OUTPATH, "w", encoding="utf-8") as fout:
        for line in fin:
            obj = json.loads(line)
            incident_id = obj.get("id")
            service = obj.get("service","")
            text = " ".join([
                obj.get("description",""),
                "Root cause: " + obj.get("root_cause",""),
                "Fixes applied: " + obj.get("fixes_applied","")
            ])
            chunks = make_chunks(text, incident_id, service)
            for c in chunks:
                fout.write(json.dumps(c, ensure_ascii=False) + "\n")
                total_chunks += 1
    print(f"Wrote {total_chunks} chunks to {OUTPATH}")

if __name__ == "__main__":
    main()
