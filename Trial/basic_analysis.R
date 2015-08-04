# This analysis script and used data belongs to a study conducted at the University of Vienna (Faculty of Computer Science, Cooperative Systems Group) in 2015.
# The description of the trial can be found in the thesis of P. Zwickl or in upcoming publications.

#==============
#  The MIT License (MIT)
#
#Copyright (c) 2015 Patrick Zwickl
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#  
#  The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#==============

#NOTE: Quality classes range in [1,8] in the raw input data, but are labelled in [0,7] in corresponding publications.
#Figures sometimes reflect the [0,7] labelling wherever functioning. A TODO is added otherwise.

find_price_per_tariff <- function(data, tariff, pmax) {
  if (pmax == 1) {
    multiplier <- 1;
  }
  else {
    multiplier <- (1.0/pmax);
  }
  
  
  prices_1 <- data[data$Tariff1==tariff,]$Price1*multiplier;
  prices_2 <- data[data$Tariff2==tariff,]$Price2*multiplier;
  prices_3 <- data[data$Tariff3==tariff,]$Price3*multiplier;
  
  prices <- append(prices_1, prices_2);
  prices <- append(prices, prices_3);
  
  return(prices)
}

find_quality_per_tariff <- function(data, tariff) {
  qualities_1 <- data[data$Tariff1==tariff,]$Quality1;
  qualities_2 <- data[data$Tariff2==tariff,]$Quality2;
  qualities_3 <- data[data$Tariff3==tariff,]$Quality3;
  
  qualities <- append(qualities_1, qualities_2);
  qualities <- append(qualities, qualities_3);

  return(qualities)
}

find_qoe_rating_per_tariff <- function(data,tariff) {
  ratings_1 <- data[data$Tariff1==tariff,]$QoE1;
  ratings_2 <- data[data$Tariff2==tariff,]$QoE2;
  ratings_3 <- data[data$Tariff3==tariff,]$QoE3;
  
  ratings <- append(ratings_1, ratings_2);
  ratings <- append(ratings, ratings_3); 
  
  return(ratings)
}

find_acceptance_per_tariff <- function(data,tariff) {
  ratings_1 <- data[data$Tariff1==tariff,]$Accept1;
  ratings_2 <- data[data$Tariff2==tariff,]$Accept2;
  ratings_3 <- data[data$Tariff3==tariff,]$Accept3;
  
  ratings <- append(ratings_1, ratings_2);
  ratings <- append(ratings, ratings_3); 
  
  return(ratings)
}


show_descriptive_statistics <- function(label, data) {
  
  print(label)
  
  cat("\nMean: ", mean(data))
  cat("\nMedian: ", median(data))
  cat("\nVariance: ", var(data))
  cat("\nStd.deviation: ", sd(data))
  cat("\nMin: ", min(data))
  cat("\nMax:", max(data))
  cat("\n")
  
}

show_advanced_statistics <- function(name, test_data1, test_data2, control_data1, control_data2) {

  
  cat("\nCOMPARISION TITLE: ", name)
  cat("\n\n")
  
  cat("Correlations:\n")
  
  cor_p_test = cor(test_data1, test_data2, method="pearson");
  cor_s_test = cor(test_data1, test_data2, method="spearman");
  
  cor_p_cont = cor(control_data1, control_data2, method="pearson");
  cor_s_cont = cor(control_data1, control_data2, method="spearman");
  
  cat("\nPearson Correlation: Test group vs. Control group: ", cor_p_test, " vs. ", cor_p_cont)
  cat("\nSpearman Correlation: Test group vs. Control group: ", cor_s_test, "vs. ", cor_s_cont)
  
  if(cor_s_test > cor_p_test) {
    cat("\nTest group correlation: Likely montone but non-linear")
  }
  if(cor_s_cont > cor_p_cont) {
    cat("\nControl group correlation: Likely montone but non-linear")
  }
  
  cat("\nANOVA RM:\n")
  
  lenT = length(test_data1);
  lenC = length(control_data1);
  time=rep(c("pre","post","pre","post"),c(lenT,lenT,lenC,lenC))
  group=rep(c("test","control"),c(2*lenT,2*lenC))
  
  # create the response variable vector
  SSS=c(test_data1,test_data2,control_data1,control_data2)
  
  subj.test = c(seq(1, lenT*2, 1))
  subj.control = c(seq(lenT*2+1, lenT*2+lenC*2, 1))
  
  subject=c(subj.test,subj.control)

  hill=data.frame(subject,group,time,SSS) # diet, test
  
  # Some summary data
  with(hill, tapply(SSS, list(group,time), mean))
  
  # Overview plot
  # TODO: Shall we save the plots in files?
  with(hill, boxplot(SSS ~ group + time))
  with(hill, boxplot(SSS ~ time + group))
  title(main="Market Entrance Data")
  title(ylab="SSS Scores")
  
  #Now really ANOVA
  aov.out = aov(SSS ~ group * time + Error(subject/time), data=hill)
  summary(aov.out)
  
  #cat("\nEND COMPARISION\n")
}

#confidence_plot
MOS_plot <- function(path_to_file, x_data, y_data) {
  x <- x_data;
  df <- data.frame(x = x_data,  y = y_data);
  
  agg_df = aggregate(y ~ x, data = df, mean)
  agg_sd = aggregate(y ~ x, data = df, sd)
  agg_sd[is.na(agg_sd)] <- 0 # There can be items with NA resuts if list length < 2
  sdev = agg_sd$y
  
  pdf(paste0(path_to_file,".pdf"))
  plot(agg_df$x, agg_df$y,
       pch=19, xlab="Quality classes", ylab="MOS / ACR-5",
       main="", ylim=c(1.0, 5.0) #Scatter plot with std.dev error bars
  )
  # hack: we draw arrows but with very special "arrowheads"
  arrows(agg_df$x, agg_df$y-sdev, agg_df$x, agg_df$y+sdev, length=0.05, angle=90, code=3)

  fit = nls(y~a*log10(x)+b, data=agg_df, start=list(a=-0.8,b=-2), trace=TRUE)
  lines(agg_df$x,predict(fit))
  
  dev.off() # save the file
  
  pdf(paste0(path_to_file,"_box.pdf"))
  boxplot(y~x,data=df, main="", #Box plot with logarithmic fit
          xlab="Quality classes", ylab="MOS / ACR-5", ylim=c(1.0,5.0))
  lines(agg_df$x,predict(fit))
  dev.off()
  
}

acceptance_plot <- function(path_to_file, qualities, acceptance) {
  df <- data.frame(x = qualities,  y = acceptance);
  pdf(paste0(path_to_file, ".pdf"));
  boxplot(y~x,data=df, main="Acceptance Box Plot", 
        xlab="Quality classes", ylab="Acceptance Rate", ylim=c(0.0,1.0));
  dev.off()
}

path_to_folder = "~/Office/WTP/2015_study/wtpstudy/analysis/" # TODO: Adapt path / our automatic download
csv_file = paste0(path_to_folder,"study2015_user-list")
raw_data = read.csv(csv_file, header = TRUE)

#########################################################
#FILTER by Tariff A
#########################################################

prices_A <- find_price_per_tariff(raw_data, "A", 1);
normalized_prices_A <- find_price_per_tariff(raw_data, "A", 2);
qualities_A <- find_quality_per_tariff(raw_data, "A");
ratings_A <- find_qoe_rating_per_tariff(raw_data, "A");
acceptance_A <- find_acceptance_per_tariff(raw_data, "A");

show_descriptive_statistics("A; Absolute", prices_A)
show_descriptive_statistics("A; Normalized", normalized_prices_A)

#########################################################
#FILTER by Tariff B
#########################################################

prices_B <- find_price_per_tariff(raw_data, "B", 1);
normalized_prices_B <- find_price_per_tariff(raw_data, "B", 3);
qualities_B <- find_quality_per_tariff(raw_data, "B");
ratings_B <- find_qoe_rating_per_tariff(raw_data, "B");
acceptance_B <- find_acceptance_per_tariff(raw_data, "B");

show_descriptive_statistics("B; Absolute", prices_B)
show_descriptive_statistics("B; Normalized", normalized_prices_B)

#########################################################
#FILTER by Tariff C
#########################################################

prices_C <- find_price_per_tariff(raw_data, "C", 1);
normalized_prices_C <- find_price_per_tariff(raw_data, "C", 4);
qualities_C <- find_quality_per_tariff(raw_data, "C");
ratings_C <- find_qoe_rating_per_tariff(raw_data, "C");
acceptance_C <- find_acceptance_per_tariff(raw_data, "C");

show_descriptive_statistics("C; Absolute", prices_C)
show_descriptive_statistics("C; Normalized", normalized_prices_C)

#########################################################
#FILTER by sequence group (macro group)
#########################################################

macro_increase = raw_data[raw_data$MacroGroup=="Increase",]
macro_control = raw_data[raw_data$MacroGroup=="Control",]

show_descriptive_statistics("Macro Increase: M2 Price:", macro_increase$Price2)
show_descriptive_statistics("Macro Control: M2 Price:", macro_control$Price2)

show_advanced_statistics("Macro Increase Vs. Control - M1 and M2 - Prices", macro_increase$Price1, macro_increase$Price2, macro_control$Price1, macro_control$Price2)

show_descriptive_statistics("Macro Increase: M2 Quality:", macro_increase$Quality1)
show_descriptive_statistics("Macro Increase: M2 Quality:", macro_increase$Quality2)
show_descriptive_statistics("Macro Increase: M2 Quality:", macro_increase$Quality3)

show_descriptive_statistics("Macro Control: M2 Quality:", macro_control$Quality1)
show_descriptive_statistics("Macro Control: M2 Quality:", macro_control$Quality2)
show_descriptive_statistics("Macro Control: M2 Quality:", macro_control$Quality3)
show_advanced_statistics("Macro Increase Vs. Control - M1 and M2 - Quality", macro_increase$Quality1, macro_increase$Quality2, macro_control$Quality1, macro_control$Quality2)

show_advanced_statistics("Macro Increase Vs. Control - M2 and M3 - Prices", macro_increase$Price1, macro_increase$Price2, macro_control$Price2, macro_control$Price3)
show_advanced_statistics("Macro Increase Vs. Control - M2 and M3 - Quality", macro_increase$Quality2, macro_increase$Quality3, macro_control$Quality1, macro_control$Quality2)


if(var(macro_increase$Quality1) > var(macro_increase$Quality2) && var(macro_control$Quality1) > var(macro_control$Quality2)) {
  cat("\nData is very noisy in the first measurement. By the design, the noise should increase when the price is altered, as people have to revise their decisions.")
  cat("Review if the correlation is almost identical:")
  cat("\nCorrelation Control:",  cor(macro_control$Quality1, macro_control$Quality2))
  cat("\nCorrelation Increase: ", cor(macro_increase$Quality1, macro_increase$Quality2))
  cat("\nIf yes, then think about adapting your design.")
}

#########################################################
#COMPARE THE TWO CONTROL GROUPS INSTEAD..
#FIRST VIDEO LEARNING PHASE => EXTEND PRACTICE TIME in OULU plus review video files again
#########################################################

group2 = raw_data[raw_data$RailsGroup=="2",] # Control group: B -> B -> A
group4 = raw_data[raw_data$RailsGroup=="4",] # Control group: B -> B -> C

show_descriptive_statistics("Control 2 - 3rd measurement - Tariff B (Absolute)", group2$Price2);
show_descriptive_statistics("Control 4 - 3rd measurement - Tariff B (Absolute)", group4$Price2);

show_descriptive_statistics("Control 2 - 3rd measurement - Tariff B (Absolute)", group2$Price3);
show_descriptive_statistics("Control 4 - 3rd measurement - Tariff B (Absolute)", group4$Price3);


show_descriptive_statistics("Control 2 - 3rd measurement - Tariff B (Normalized)", (group2$Quality2-1)/7);
show_descriptive_statistics("Control 4 - 3rd measurement - Tariff B (Normalized)", (group4$Quality2-1)/7);

show_descriptive_statistics("Control 2 - 3rd measurement - Tariff A", (group2$Quality3-1)/7);
show_descriptive_statistics("Control 4 - 3rd measurement - Tariff C", (group4$Quality3-1)/7);
  
show_advanced_statistics("Control group 2 vs. control group 4; M2 and M3; Quality instead of Price", group2$Quality2, group2$Quality3, group4$Quality2, group4$Quality3)

#########################################################
# PER MEASUREMENT M1, M2, M3
#########################################################

#M1
show_descriptive_statistics("All over all (absolute)", raw_data$Price1);
show_descriptive_statistics("All over all (absolute)", (raw_data$Quality1-1)/7); # Quality level is transferred to [0,1]


#M2
show_descriptive_statistics("All over all (absolute)", raw_data$Price2);
show_descriptive_statistics("All over all (absolute)", (raw_data$Quality2-1)/7);

#M3
show_descriptive_statistics("All over all (absolute)", raw_data$Price3);
show_descriptive_statistics("All over all (absolute)", (raw_data$Quality3-1)/7);

#########################################################
# Histogram of all
#########################################################

all_normalized_prices = append(append(normalized_prices_A, normalized_prices_B), normalized_prices_A)
all_prices = append(append(raw_data$Price1,raw_data$Price2),raw_data$Price3)
all_qualities = append(append(raw_data$Quality1,raw_data$Quality2),raw_data$Quality3)
all_acceptance = append(append(raw_data$Accept1,raw_data$Accept2),raw_data$Accept3)
all_ratings = append(append(raw_data$QoE1,raw_data$QoE2),raw_data$QoE3)

pdf(paste0(path_to_folder,"his_all_prices.pdf"))
hist(all_prices, xlab = "Normalised expenditures (per video)", ylab="Total", main="")
dev.off()
pdf(paste0(path_to_folder,"his_all_qualities.pdf"))
hist(all_qualities-1, xlab = "", ylab="Total", main="") # subtraction of 1 required for using the q_0 to q_7 notion .. Normalised expenditures (per video)
dev.off()
pdf(paste0(path_to_folder,"his_all_norm_prices.pdf"))
hist(all_normalized_prices, xlab = "", ylab="Total", main="") # Normalised expenditures (per video)
dev.off()

show_descriptive_statistics("All over all (absolute)", all_prices);
show_descriptive_statistics("All over all (normalized)", all_normalized_prices);

##########################################################################
##################################  QoE ##################################
##########################################################################

# Let's start with M2 where all are on tariff B
dat <- aggregate(QoE2 ~ Quality2, raw_data, mean)
mos_m2_plain_file = paste0(path_to_folder,"mos_m2_plain.pdf")
pdf(mos_m2_plain_file)
plot(as.factor(dat$Quality2), dat$QoE2)
dev.off()

mos_m2_error_file = paste0(path_to_folder,"mos_m2_error.pdf")
MOS_plot(mos_m2_error_file, raw_data$Quality2, raw_data$QoE2)  # TODO: -1 missing (as for all MOS_PLOT)

# Let's now look at the two different groups (increase and control):
dat_inc <- aggregate(QoE2 ~ Quality2, macro_increase, mean)
mos_inc_plain_file = paste0(path_to_folder,"mos_inc_plain.pdf")
pdf(mos_inc_plain_file)
plot(as.factor(dat_inc$Quality2-1), dat_inc$QoE2)
dev.off()

dat_cont <- aggregate(QoE2 ~ Quality2, macro_control, mean)
mos_cont_plain_file = paste0(path_to_folder,"mos_cont_plain.pdf")
pdf(mos_cont_plain_file)
plot(as.factor(dat_cont$Quality2-1), dat_cont$QoE2)
dev.off()

mos_cont_error_file = paste0(path_to_folder,"mos_cont_error.pdf")
MOS_plot(mos_cont_error_file, macro_control$Quality2, macro_control$QoE2) #TODO: -1

mos_inc_error_file = paste0(path_to_folder,"mos_inc_error.pdf")
MOS_plot(mos_inc_error_file, macro_increase$Quality2, macro_increase$QoE2) #TODO: -1

# NOW MOS PER TARIFF

mos_cont_error_file = paste0(path_to_folder,"mos_tariff_A")
MOS_plot(mos_cont_error_file, qualities_A, ratings_A) # TODO: -1

mos_cont_error_file = paste0(path_to_folder,"mos_tariff_B")
MOS_plot(mos_cont_error_file, qualities_B, ratings_B) # TODO: -1

mos_cont_error_file = paste0(path_to_folder,"mos_tariff_C")
MOS_plot(mos_cont_error_file, qualities_C, ratings_C) # TODO: -1

qualities_all = append(append(qualities_A,qualities_B),qualities_C)
ratings_all = append(append(ratings_A,ratings_B),ratings_C)
mos_tariff_all = paste0(path_to_folder,"mos_tariff_all")
MOS_plot(mos_tariff_all, qualities_all, ratings_all) # TODO: -1

# NOW Acceptance General + PER TARIFF
# WARNING: Quality classes are minus 1 here already!
acceptance_plot(paste0(path_to_folder,"accept_A"), qualities_A-1, acceptance_A);
acceptance_plot(paste0(path_to_folder,"accept_B"), qualities_B-1, acceptance_B);
acceptance_plot(paste0(path_to_folder,"accept_C"), qualities_C-1, acceptance_C);

acceptance_plot(paste0(path_to_folder,"accept_all"), all_qualities-1, all_acceptance);

##########################################################################
########################  Likability & Own Money #########################
##########################################################################

# Did you like the content? (not the quality of the video)

all_likeability = c(raw_data$Like1, raw_data$Like2, raw_data$Like3);
cat("\nContent likability:", mean(all_likeability)*100, " (% of watched videos)");

# Did it feel like spending your own money?

own_money = raw_data$OwnMoney
cat("\nOwn money feeling (average):", mean(own_money), " (one vote per user)");
cat("\nOwn money feeling (median):", median(own_money), " (one vote per user)");
