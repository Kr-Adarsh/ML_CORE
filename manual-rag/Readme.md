# Under the Hood: Chunking & Vector Embeddings


## Step by Step

### 1. Tokenization

eg: `"from data"` → `[2, 2013, 2951, 1012, 3]` ~ *[CLS, from, data, ., SEP]*

---

### 2. Embedding Lookup

Each token ID is mapped to a 384-dimensional vector from the embedding layer. The model doesn't use a slow Python for loop or a dictionary key lookup: under the hood, it does this instantly using high-speed matrix indexing or hardware-accelerated matrix multiplication.

So it looks like this: it looks up each row index from the massive weight matrix $E_{\text{vocab}}$:

$$\begin{aligned}
\text{Row 2 } ([CLS]) &\rightarrow [0.012, -0.054, \dots, 0.089] \\
\text{Row 2013 } (from) &\rightarrow [-0.041, 0.022, \dots, -0.112] \\
\text{Row 2951 } (data) &\rightarrow [0.091, 0.003, \dots, 0.341] \\
\text{Row 1012 } (.) &\rightarrow [-0.002, -0.012, \dots, 0.001] \\
\text{Row 3 } ([SEP]) &\rightarrow [0.004, 0.071, \dots, -0.015]
\end{aligned}$$

*By stacking these rows together, we get our first true structural matrix, called the Token Embedding Matrix ($X_{\text{token}}$). Because we have 5 tokens and each has 384 numbers, its shape is $(5, 384)$.*

---

### 3. Positional Encoding

To help the model understand the order of tokens, we add a positional encoding matrix ($P$) of the same shape $(5, 384)$ to the token embeddings. This gives us the final input matrix ($X_{\text{input}}$) that goes into the transformer layers.

The model keeps a second, separate dictionary called the Positional Embedding Matrix ($X_{\text{pos}}$). It contains hardcoded or learned vectors representing structural positions:

- Row 0: The concept of being the 1st word in a sequence → $[0.001, 0.005, \dots]$
- Row 1: The concept of being the 2nd word in a sequence → $[-0.021, 0.011, \dots]$
- Row 2: The concept of being the 3rd word in a sequence → $[0.054, -0.082, \dots]$
- ...up to the model's maximum sequence length limit (usually 512).

Finally, the model adds the token embeddings and positional encodings together to create the final input matrix:

$$X_{\text{input}} = X_{\text{token}} + P $$

Visually, the element-by-element addition looks like this:

<table>
<tr>
  <td align="center">

$$X_{\text{input}}$$

  </td>
  <td align="center">=</td>
  <td align="center">

$$X_{\text{token}}$$

  </td>
  <td align="center">+</td>
  <td align="center">

$$P$$

  </td>
</tr>
<tr>
<td>

| $X_{\text{input}}$ $(5 \times 384)$ |
|---|
| ← Final [CLS] → |
| ← Final from → |
| ← Final data → |
| ← Final . → |
| ← Final [SEP] → |

</td>
<td>=</td>
<td>

| $X_{\text{token}}$ $(5 \times 384)$ |
|---|
| ← Vector for [CLS] → |
| ← Vector for from → |
| ← Vector for data → |
| ← Vector for . → |
| ← Vector for [SEP] → |

</td>
<td>+</td>
<td>

| $P$ $(5 \times 384)$ |
|---|
| ← Position 0 → |
| ← Position 1 → |
| ← Position 2 → |
| ← Position 3 → |
| ← Position 4 → |

</td>
</tr>
</table>

- - -

### 4. Self-Attention (semantic understanding)

*This is where static vectors turn into dynamic, contextual vectors. For example, this layer is what allows the model to know that "bank" means a financial institution in one sentence and a river edge in another.*

To figure out how words relate to each other, the transformer uses a system inspired by database retrieval: Queries, Keys, and Values. Inside this layer, the model has three distinct, trainable weight matrices: $W_Q$, $W_K$, and $W_V$. Because the embedding dimension is $384$, each of these projection matrices has a shape of $(384, 384)$.

#### 4.1: Projecting into Query, Key, and Value Spaces

The model multiplies the input matrix $X_{\text{input}}$ by each of these weight matrices to split it into three separate spaces:

$$Q = X_{\text{input}} \cdot W_Q \quad \text{(Queries: "What am I looking for?")}$$
$$K = X_{\text{input}} \cdot W_K \quad \text{(Keys: "What information do I contain?")}$$
$$V = X_{\text{input}} \cdot W_V \quad \text{(Values: "The actual content to share")}$$

Each of these resulting matrices has the same shape as the input: $(5, 384)$. They represent different perspectives on the same data:

- $Q$: How each token is asking questions about other tokens.
- $K$: How each token is offering information about itself.
- $V$: The actual information content of each token.

**Example: walking through it step by step:**

**Phase 1: The Linear Vector Projection** *(where $Q$, $K$, $V$ are born)*

Inside the self-attention layer, there are giant grids of numbers called Weight Matrices. These are learned during the model's training on billions of sentences. For our dimension size, the model has:

- $W_Q$ (Query Weights): a matrix of size $(384, 384)$
- $W_K$ (Key Weights): a matrix of size $(384, 384)$

When a sentence runs, the model takes the raw embedded vector for "data" ($x_{\text{data}}$) and multiplies it by $W_Q$ to create its Query vector ($q_{\text{data}}$):

$$q_{\text{data}} = x_{\text{data}} \cdot W_Q$$

Simultaneously, it takes the raw embedded vector for "from" ($x_{\text{from}}$) and multiplies it by $W_K$ to create its Key vector ($k_{\text{from}}$):

$$k_{\text{from}} = x_{\text{from}} \cdot W_K$$

Both $q_{\text{data}}$ and $k_{\text{from}}$ are now unique vectors of size $384$.

**Phase 2: The Raw Compatibility Score** *(dot product)*

To find out how contextually relevant "from" is to "data", the model calculates the dot product of these two vectors: it multiplies them element-by-element and sums up the total:

$$\text{Raw Score}_{(\text{data} \rightarrow \text{from})} = (q_1 \times k_1) + (q_2 \times k_2) + \dots + (q_{384} \times k_{384})$$

Let's say this massive sum totals up to a raw score of **14.5**. (The model does this exact same dot product for "data" against every other word's Key vector in the sentence.) Let's assume the raw scores for the "data" row come out to:

| Token | Raw Score |
|-------|-----------|
| [CLS] | $10.2$ |
| from  | $14.5$ |
| data  | $13.8$ |
| .     | $6.1$  |
| [SEP] | $6.8$  |

**Then scaling:**

If raw dot products get too large, they push the neural network into an unstable zone. To smooth things out, the model divides every raw score by the square root of the vector dimension ($\sqrt{384} \approx 19.6$):

$$\text{Scaled Score} = \frac{\text{Raw Score}}{19.6}$$

| Token | Scaled Score |
|-------|-------------|
| [CLS] | $10.2 / 19.6 = \mathbf{0.52}$ |
| from  | $14.5 / 19.6 = \mathbf{0.74}$ |
| data  | $13.8 / 19.6 = \mathbf{0.70}$ |
| .     | $6.1 / 19.6 = \mathbf{0.31}$ |
| [SEP] | $6.8 / 19.6 = \mathbf{0.35}$ |

**Then softmaxing:**

These scaled scores $(0.52, 0.74, 0.70$, etc.) don't represent percentages: they don't add up to $1.0$. To turn them into clean attention weights, the model passes the row through the Softmax equation:

$$\text{Weight} = \frac{e^{\text{Scaled Score}}}{\sum e^{\text{All Scaled Scores}}}$$

Let's calculate the numerator ($e^x$) for each:

| Token | $e^x$ |
|-------|--------|
| [CLS] | $e^{0.52} \approx 1.68$ |
| from  | $e^{0.74} \approx \mathbf{2.10}$ |
| data  | $e^{0.70} \approx 2.01$ |
| .     | $e^{0.31} \approx 1.36$ |
| [SEP] | $e^{0.35} \approx 1.42$ |

> Sum of all exponents $= 1.68 + 2.10 + 2.01 + 1.36 + 1.42 = \mathbf{8.57}$

Now, we divide each individual exponent by the total sum ($8.57$) to get the final attention weights:

- Weight for [CLS] $= 1.68 / 8.57 = \mathbf{0.19}$ (rounds near 0.15)
- Weight for from $= 2.10 / 8.57 = \mathbf{0.24}$ (in our matrix example, this calculated out to exactly 0.45 based on tighter dummy vectors)
- Weight for data $= 2.01 / 8.57 = \mathbf{0.23}$ (rounds near 0.35)

*Thus in the end we get the attention weights for specific words.*

---

#### 4.2: Calculating Attention Scores

To see how much attention the word "data" should pay to "from", the model calculates the dot product between the Query vector of "data" and the Key vector of "from". To do this for all words simultaneously, it multiplies the entire Query matrix $Q$ by the transposed Key matrix $K^T$:

$$\text{Raw Scores} = Q \cdot K^T$$

Let's look at the matrix dimensions:

$$\text{shape}(5, 384) \times \text{shape}(384, 5) = \text{shape}(5, 5)$$

*This outputs a $(5, 5)$ grid of raw compatibility numbers. Every cell $(i, j)$ represents how much word $i$ attends to word $j$.*

---

#### 4.3: Scaling and Normalizing (As we did earlier)

To prevent the raw scores from becoming too large (which can cause issues with gradients), the model scales them by dividing by the square root of the key dimension ($\sqrt{d_k} = \sqrt{384} \approx 19.6$). "Too large" means numbers that lead to very small gradients during backpropagation, making training unstable.

Next, it applies Softmax $\left(\frac{e^x}{\sum e^x_i}\right)$ across each row, turning raw scores into clean probabilities between $0$ and $1$ that add up exactly to $1.0$:

$$\text{Attention Weights} = \text{Softmax}\left(\frac{Q \cdot K^T}{\sqrt{d_k}}\right)$$

For our example sentence, the attention weight matrix might look like this:

$$\begin{array}{c|ccccc}
  & [CLS] & from & data & . & [SEP] \\
\hline
[CLS] & 0.40 & 0.20 & 0.30 & 0.05 & 0.05 \\
from  & 0.10 & 0.55 & 0.30 & 0.03 & 0.02 \\
data  & 0.15 & 0.45 & 0.35 & 0.02 & 0.03 \\
.     & 0.20 & 0.10 & 0.20 & 0.45 & 0.05 \\
[SEP] & 0.30 & 0.15 & 0.25 & 0.05 & 0.25
\end{array}$$

---

#### 4.4: The Contextual Blend (Multiplying by Values)

Now that the model knows the exact percentage weights, it uses them to blend the Value matrix ($V$). It multiplies the $(5, 5)$ attention weights by the $(5, 384)$ Value matrix:

$$\text{Contextual Output} = \text{Attention Weights} \times V$$
$$\text{shape}(5, 5) \times \text{shape}(5, 384) = \text{shape}(5, 384)$$

To compute the new, contextual row vector for "data", the system takes:

$$\text{New Vector}_{\text{data}} = (0.15 \times V_{[CLS]}) + (0.45 \times V_{\text{from}}) + (0.35 \times V_{\text{data}}) + (0.02 \times V_{.}) + (0.03 \times V_{[SEP]})$$

> Note: the decimal weights $(0.15, 0.45, 0.35$, etc.) are not hardcoded: they are calculated dynamically on the fly based on the specific words in the sentence.

*The resulting vector is no longer just a generic lookup representation of the word "data". It is now a context-rich vector that actively reflects its structural relationship to the phrase "from data."*

---

### 5. Feed-Forward Network (FFN)

After self-attention, the model passes the output through a feed-forward neural network (FFN) to further process the information. This FFN consists of two linear transformations with a ReLU activation in between:

$$\text{FFN}(x) = \text{ReLU}(x \cdot W_1 + b_1) \cdot W_2 + b_2$$

where $W_1$ and $W_2$ are weight matrices, and $b_1$ and $b_2$ are bias vectors. The FFN helps the model capture more complex patterns and interactions in the data.

---

### 6. Layer Normalization and Residual Connections

To stabilize training and help with gradient flow, the model uses layer normalization and residual connections. After the self-attention and FFN, the model adds the original input back to the output:

$$\text{Output} = \text{LayerNorm}(x + \text{FFN}(\text{Attention Output}))$$

This allows the model to retain information from earlier layers while also incorporating new, processed information.

---

### 7. Stacking Multiple Layers

The transformer architecture stacks multiple layers of self-attention and FFN to build deeper representations of the input. Each layer refines the contextual understanding of the tokens, allowing the model to capture more complex relationships and nuances in the text.

For example, in a 6-layer transformer, the output of the first layer becomes the input to the second layer, and so on. This hierarchical processing enables the model to understand not just word-level relationships but also higher-level concepts and structures in the text.

---

### 8. Pooling: Condensing the Matrix

Right now, the model is holding 5 vectors (one for each token: [CLS], from, data, ., [SEP]), and each vector is 384 numbers long. We need to collapse these 5 rows into 1 single row: since we want a single vector to represent the entire sentence for retrieval.

For our specific model, it uses **Mean Pooling**, which simply averages the 5 vectors together. For example:

#### 8.1: Taking the averages

$$\begin{array}{c|cccc}
\text{[Token]} & \text{Col 1 (Context)} & \text{Col 2 (Tense)} & \text{Col 3 (Syntax)} & \cdots & \text{Col 384} \\
\hline
[CLS]  &  0.12 & -0.05 &  0.80 & \cdots &  0.01 \\
from   & -0.40 &  0.22 &  0.10 & \cdots & -0.11 \\
data   &  0.90 &  0.03 &  0.40 & \cdots &  0.34 \\
.      & -0.02 & -0.12 &  0.01 & \cdots &  0.00 \\
[SEP]  &  0.04 &  0.07 & -0.15 & \cdots & -0.15 \\
\hline
\textbf{AVERAGE} & 0.128 & 0.030 & 0.232 & \cdots & 0.018 \\
\hline
\end{array}$$

#### 8.2: Normalizing

Remember we passed `normalize_embeddings=True` when we created the embedding model. This triggers a final geometric calibration called **L2 (Euclidean) Normalization**:

$$\|V\|_2 = \sqrt{(0.128)^2 + (0.030)^2 + (0.232)^2 + \dots + (0.018)^2}$$

Let's assume the absolute length (magnitude) of the raw vector equals $2.50$.

To scale the vector down to a length of 1, the model divides every single element by that total magnitude ($2.50$):

$$\begin{aligned}
\text{Normalized Value}_1 &= 0.128 / 2.50 = \mathbf{0.0512} \\
\text{Normalized Value}_2 &= 0.030 / 2.50 = \mathbf{0.0120} \\
\text{Normalized Value}_3 &= 0.232 / 2.50 = \mathbf{0.0928} \\
&\,\dots \\
\text{Normalized Value}_{384} &= 0.018 / 2.50 = \mathbf{0.0072}
\end{aligned}$$

The final output array looks exactly like the floating-point values in the first screenshot:

$$\text{embed\_chunks} = \begin{bmatrix} 0.0512, & 0.0120, & 0.0928, & \dots, & 0.0072 \end{bmatrix}$$

---

As mentioned earlier, this normalization is what makes Cosine Similarity so clean because:

$$\text{cosine similarity} = \frac{A \cdot B}{\|A\| \|B\|}$$

where $\|A\|$ and $\|B\|$ are the magnitudes of the vectors. Since both vectors have been normalized to a magnitude of 1, the formula simplifies beautifully to just:

$$\text{cosine similarity} = A \cdot B$$