import torch
from transformers import (
    AutoTokenizer,
    AutoModel,
)


class AttentionGetter:
    def __init__(self, model_name: str):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModel.from_pretrained(model_name, output_attentions=True).to(
            self.device
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _grab_attn(self, context):
        # Run Forward Pass
        output = self.model(context)
        # Grab the attention from the output
        # Format as Layer x Head x From x To
        attn = torch.cat([l for l in output[-1]], dim=0)
        format_attn = [
            [
                [[str(round(att * 100)) for att in head] for head in layer]
                for layer in tok
            ]
            for tok in attn.cpu().tolist()
        ]
        return format_attn

    def gpt_analyze_text(self, text: str):
        # Process Input
        toked = self.tokenizer.encode(text)
        # Convert to PyTorch Tensor
        start_token = torch.full(
            (1, 1), self.tokenizer.bos_token_id, device=self.device, dtype=torch.long,
        )
        context = torch.tensor(toked, device=self.device, dtype=torch.long).unsqueeze(0)
        context = torch.cat([start_token, context], dim=1)
        attn = self._grab_attn(context)

        return {
            "tokens": self.tokenizer.convert_ids_to_tokens(context[0]),
            "attention": attn,
        }

    def bert_analyze_text(self, text: str):
        """Works for BERT models"""
        toked = self.tokenizer.encode(text)
        context = torch.tensor(toked).unsqueeze(0).long()
        attn = self._grab_attn(context)

        return {
            "tokens": self.tokenizer.convert_ids_to_tokens(toked),
            "attention": attn,
        }


if __name__ == "__main__":
    model = AttentionGetter("gpt2")
    payload = model.gpt_analyze_text("This is a test.")
    print(payload)

    model = AttentionGetter("distilbert-base-uncased")
    payload = model.bert_analyze_text("This is a test.")
    print(payload)

    print("checking successful!")
