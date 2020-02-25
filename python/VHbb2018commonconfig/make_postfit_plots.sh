#!/bin/bash
echo "usage: $0 path/to/FitDiagnostics.root name"
echo "this will create DNN postfit plots!"

./submit.py -T Zvv2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS_NoQCD!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_fit_s;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitCRDNN_BKG.log:=True;plotDef:postfitCRDNN_BKG.log:=True;plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="Zhf_medhigh_Znn,SR_medhigh_Znn,Zlf_medhigh_Znn+ttbar_medhigh_Znn"
./submit.py -T Zvv2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS_NoQCD!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_prefit;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitCRDNN_BKG.log:=True;plotDef:postfitCRDNN_BKG.log:=True;plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="Zhf_medhigh_Znn,SR_medhigh_Znn,Zlf_medhigh_Znn+ttbar_medhigh_Znn"

./submit.py -T Wlv2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;plotDef:postfitMultiDNNbackground.log:=True;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_fit_s;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="Whf_medhigh_Wmn,Whf_medhigh_Wen,SR_medhigh_Wmn,SR_medhigh_Wen,Wlf_medhigh_Wmn+ttbar_medhigh_Wmn,Wlf_medhigh_Wen+ttbar_medhigh_Wen"
./submit.py -T Wlv2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;plotDef:postfitMultiDNNbackground.log:=True;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_prefit;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="Whf_medhigh_Wmn,Whf_medhigh_Wen,SR_medhigh_Wmn,SR_medhigh_Wen,Wlf_medhigh_Wmn+ttbar_medhigh_Wmn,Wlf_medhigh_Wen+ttbar_medhigh_Wen"

./submit.py -T Zll2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;plotDef:postfitMultiDNNbackground.log:=True;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_fit_s;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="SR_low_Zee,SR_low_Zmm,SR_medhigh_Zee,SR_medhigh_Zmm,Zhf_low_Zee,Zhf_low_Zmm,Zhf_medhigh_Zee,Zhf_medhigh_Zmm,Zlf_low_Zee+ttbar_low_Zee,Zlf_low_Zmm+ttbar_low_Zmm,Zlf_medhigh_Zee+ttbar_medhigh_Zee,Zlf_medhigh_Zmm+ttbar_medhigh_Zmm"
./submit.py -T Zll2017 -J postfitplot --set='LimitGeneral.setup=<!LimitGeneral|setup_NoSTXS!>;LimitGeneral.Group=<!VHbbCommon|GroupNoSTXS!>;plotDef:postfitMultiDNNbackground.log:=True;Fit.FitDiagnosticsDump:='$1';Fit.FitType:=shapes_prefit;Plot_general.mcUncertaintyLegend:="MC uncert.";plotDef:postfitNormalization.log=False;plotDef:postfitNormalization.nBins=2;plotDef:postfitNormalization.max=2;plotDef:postfitNormalization.min=0;plotDef:postfitNormalization.xAxis=CR' --local -F postfit_$2 --region="SR_low_Zee,SR_low_Zmm,SR_medhigh_Zee,SR_medhigh_Zmm,Zhf_low_Zee,Zhf_low_Zmm,Zhf_medhigh_Zee,Zhf_medhigh_Zmm,Zlf_low_Zee+ttbar_low_Zee,Zlf_low_Zmm+ttbar_low_Zmm,Zlf_medhigh_Zee+ttbar_medhigh_Zee,Zlf_medhigh_Zmm+ttbar_medhigh_Zmm"

mkdir postfit_$2
cp logs_Zll2017/postfit_$2/Plots/* postfit_$2/
cp logs_Zvv2017/postfit_$2/Plots/* postfit_$2/
cp logs_Wlv2017/postfit_$2/Plots/* postfit_$2/
