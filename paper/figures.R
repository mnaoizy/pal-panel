# Paper figures: ggplot2 default theme, column width.
suppressPackageStartupMessages({library(ggplot2); library(ggrepel); library(jsonlite)})
root <- normalizePath(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))), ".."))
dev <- fromJSON(file.path(root, "results/stage1_dev.json"))
pl <- dev$per_listener
d <- data.frame(listener = names(pl),
                error = sapply(pl, function(v) v$mean_error),
                r = sapply(pl, function(v) v$accuracy),
                family = sapply(pl, function(v) v$family), stringsAsFactors = FALSE)
fam_labels <- c("gmm-hmm" = "GMM-HMM", "kaldi-hybrid" = "Kaldi hybrid", "conv-ctc" = "Conv. CTC",
                "ssl-ctc-librispeech" = "SSL CTC (LibriSpeech)", "ssl-ctc-other-domain" = "SSL CTC (other data)",
                "whisper" = "Whisper", "other-enc-dec" = "Other enc-dec", "transducer" = "Transducer",
                "speech-llm" = "Speech LLM", "phone-recognizer" = "Phone recognizer")
d$family <- factor(fam_labels[d$family], levels = fam_labels)
panel_r <- dev$panel_equal_mean$accuracy$r
label_set <- c("hubert-large", "jasper", "vosk-small", "crisperwhisper", "qwen2audio", "canary-1b",
               "seamless-m4t-v2", "moonshine-base", "espeak-phone", "sphinx-enus", "allosaurus-eng", "atc-xlsr")
d$label <- ifelse(d$listener %in% label_set, d$listener, "")
p1 <- ggplot(d, aes(error, r)) +
  geom_hline(yintercept = panel_r, linetype = "dashed") +
  annotate("text", x = 0.115, y = panel_r, label = "full panel", vjust = -0.5, hjust = 0, size = 2.8) +
  geom_point(aes(colour = family, shape = family), size = 2.4, stroke = 0.9) +
  geom_text_repel(aes(label = label), size = 2.3, max.overlaps = Inf, segment.size = 0.25, segment.colour = "grey40",
                  box.padding = 0.35, point.padding = 0.3, min.segment.length = 0.15, seed = 11, force = 2) +
  scale_shape_manual(values = c(15, 16, 17, 18, 5, 8, 3, 4, 7, 6)) +
  scale_x_log10(breaks = c(0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7)) +
  scale_y_continuous(limits = c(0.38, 0.78)) +
  labs(x = "Mean phoneme error rate (training split, log scale)", y = expression(italic(r)~"with accuracy rating"),
       colour = NULL, shape = NULL) +
  theme(legend.position = "bottom", legend.text = element_text(size = 6.5), legend.key.size = unit(3, "mm"),
        legend.margin = margin(0, 0, 0, 0), axis.title = element_text(size = 8.5), axis.text = element_text(size = 7.5)) +
  guides(colour = guide_legend(ncol = 2), shape = guide_legend(ncol = 2))
ggsave(file.path(root, "paper/figures/listeners.pdf"), p1, width = 3.45, height = 2.9, units = "in")

s5 <- fromJSON(file.path(root, "results/stage5.json"))
raw <- read.csv("/Volumes/Untitled/Prj/gop/data/allsstar/L2_response_score.csv", stringsAsFactors = FALSE)
raw$speaker <- paste0(raw$nativelanguage, "_", as.integer(sub(".*ALL_(\\d+)_.*", "\\1", raw$audio)))
human <- tapply(raw$percorrect, raw$speaker, mean)
a <- data.frame(score = unlist(s5$talker_scores), human = human[names(s5$talker_scores)])
p2 <- ggplot(a, aes(score, human)) +
  geom_smooth(method = "lm", formula = y ~ x, colour = "black", linewidth = 0.6, fill = "grey70") +
  geom_point(size = 1.6, shape = 21, fill = "white") +
  labs(x = "PAL score (mean −PER, 28 listeners)", y = "Human word recovery (%)") +
  theme(axis.title = element_text(size = 8.5), axis.text = element_text(size = 7.5))
ggsave(file.path(root, "paper/figures/allsstar.pdf"), p2, width = 3.45, height = 1.95, units = "in")
cat("figures written; r =", cor(a$score, a$human), "\n")
