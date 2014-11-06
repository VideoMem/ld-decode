vector<double> c_deemp_b = {9.075768293948128e-03, -8.237285180536874e-03, 1.525400109890641e-01, 1.271261981795985e-02, -1.772601911252877e-03, -5.061921080347066e-03, -5.526588869733499e-03, -5.112432800144701e-03, -4.491518795193911e-03, };
vector <double> c_deemp_a = {1.000000000000000e+00, -2.739289771643778e-01, -1.628794813742291e-01, -1.018574697801082e-01, -6.551811195197693e-02, -4.321668274634510e-02, -2.921443695973032e-02, -1.747512379029513e-02, -1.518230676503862e-02, };

Filter f_deemp(c_deemp_b, c_deemp_a);

vector<double> c_deemp10_b = {5.033030306263742e-02, 1.326615246049396e-01, -4.699753787161509e-02, -5.387607463636233e-03, 3.034857259022750e-03, 4.993124726086266e-03, 5.003608995847797e-03, 4.444995350933708e-03, 3.754281167962590e-03, };
vector <double> c_deemp10_a = {1.000000000000000e+00, -2.556876643286093e-01, -1.528934687661787e-01, -8.597146102900972e-02, -4.577471369551848e-02, -2.260746572729532e-02, -9.521446563288450e-03, -1.552858509482608e-03, -7.850714120476686e-04, };

Filter f_deemp10(c_deemp10_b, c_deemp10_a);

vector<double> c_boost_b = {4.387575368399079e-04, 1.632895622862064e-03, 2.537748875966842e-03, 2.044228963833119e-03, -1.184428038595139e-03, -6.824725464908459e-03, -1.141112158933924e-02, -9.361696552715499e-03, 2.990718843871224e-03, 2.256903353665731e-02, 3.778448293341900e-02, 3.256028527533293e-02, -4.803881013164027e-03, -7.274845926804284e-02, -1.535119715490025e-01, -2.191957296541931e-01, 7.556710529176593e-01, -2.191957296541931e-01, -1.535119715490025e-01, -7.274845926804284e-02, -4.803881013164027e-03, 3.256028527533293e-02, 3.778448293341902e-02, 2.256903353665732e-02, 2.990718843871224e-03, -9.361696552715499e-03, -1.141112158933924e-02, -6.824725464908464e-03, -1.184428038595140e-03, 2.044228963833119e-03, 2.537748875966844e-03, 1.632895622862065e-03, 4.387575368399079e-04, };
vector <double> c_boost_a = {1.000000000000000e+00, };

Filter f_boost(c_boost_b, c_boost_a);

vector<double> c_boost10_b = {6.263255080839851e-04, -3.915507880949285e-04, -1.916735209842007e-03, -3.819172995004062e-03, -5.042485617935914e-03, -3.758388089387949e-03, 1.610695988129703e-03, 1.088981776984434e-02, 2.102516852905989e-02, 2.621377901216245e-02, 1.965771061382472e-02, -3.529284119720892e-03, -4.347367318614238e-02, -9.417406914481027e-02, -1.445325546844917e-01, -1.816730616404485e-01, 8.036072361277076e-01, -1.816730616404485e-01, -1.445325546844917e-01, -9.417406914481027e-02, -4.347367318614238e-02, -3.529284119720892e-03, 1.965771061382473e-02, 2.621377901216247e-02, 2.102516852905989e-02, 1.088981776984434e-02, 1.610695988129703e-03, -3.758388089387952e-03, -5.042485617935914e-03, -3.819172995004062e-03, -1.916735209842009e-03, -3.915507880949287e-04, 6.263255080839851e-04, };
vector <double> c_boost10_a = {1.000000000000000e+00, };

Filter f_boost10(c_boost10_b, c_boost10_a);

vector<double> c_color_b = {4.296424055924472e-03, 4.820368376227812e-03, 6.300710847429372e-03, 8.706323730295659e-03, 1.196573459156953e-02, 1.596958998357159e-02, 2.057483967978480e-02, 2.561047195098441e-02, 3.088455666359826e-02, 3.619229008456978e-02, 4.132468628021605e-02, 4.607752734167055e-02, 5.026017002027362e-02, 5.370381051353325e-02, 5.626883200069820e-02, 5.785090007668063e-02, 5.838552760594402e-02, 5.785090007668063e-02, 5.626883200069820e-02, 5.370381051353325e-02, 5.026017002027363e-02, 4.607752734167055e-02, 4.132468628021606e-02, 3.619229008456978e-02, 3.088455666359827e-02, 2.561047195098441e-02, 2.057483967978480e-02, 1.596958998357160e-02, 1.196573459156954e-02, 8.706323730295659e-03, 6.300710847429379e-03, 4.820368376227816e-03, 4.296424055924472e-03, };
vector <double> c_color_a = {1.000000000000000e+00, };

Filter f_color(c_color_b, c_color_a);

vector<double> c_lpf_b = {-1.676812318972605e-03, -5.374936889747954e-04, 2.254940908923396e-03, 4.022274254815428e-03, -1.073502430983471e-04, -9.045704503701428e-03, -1.052619532644138e-02, 5.739018325719546e-03, 2.654003770829400e-02, 1.932369268654869e-02, -2.683398362195290e-02, -6.680566651536425e-02, -2.689580509531039e-02, 1.159324474560186e-01, 2.868022627927465e-01, 3.636286743614999e-01, 2.868022627927465e-01, 1.159324474560186e-01, -2.689580509531039e-02, -6.680566651536426e-02, -2.683398362195291e-02, 1.932369268654870e-02, 2.654003770829402e-02, 5.739018325719549e-03, -1.052619532644138e-02, -9.045704503701428e-03, -1.073502430983470e-04, 4.022274254815429e-03, 2.254940908923395e-03, -5.374936889747954e-04, -1.676812318972605e-03, };
vector <double> c_lpf_a = {1.000000000000000e+00, };

Filter f_lpf(c_lpf_b, c_lpf_a);

vector<double> c_lpf42_b = {1.613172645086047e-03, 6.727619992811482e-04, -1.621472972157979e-03, -4.439803146181067e-03, -4.386700689000996e-03, 2.049823178361325e-03, 1.272098110625865e-02, 1.733049859690709e-02, 4.455855663190381e-03, -2.475177666520114e-02, -4.870918525511100e-02, -3.491898896829458e-02, 3.559709425123384e-02, 1.470689789837514e-01, 2.507784566649504e-01, 2.930806092138533e-01, 2.507784566649504e-01, 1.470689789837514e-01, 3.559709425123385e-02, -3.491898896829459e-02, -4.870918525511102e-02, -2.475177666520115e-02, 4.455855663190384e-03, 1.733049859690710e-02, 1.272098110625865e-02, 2.049823178361325e-03, -4.386700689000995e-03, -4.439803146181068e-03, -1.621472972157979e-03, 6.727619992811482e-04, 1.613172645086047e-03, };
vector <double> c_lpf42_a = {1.000000000000000e+00, };

Filter f_lpf42(c_lpf42_b, c_lpf42_a);

vector<double> c_lpf10h_b = {-6.435871671502849e-04, -3.150057733488437e-04, 2.045080082468669e-04, 1.233293769907379e-03, 3.109782673001019e-03, 6.140246552700073e-03, 1.054583615321984e-02, 1.641655403173896e-02, 2.367919781235186e-02, 3.208466075330588e-02, 4.121749748277346e-02, 5.052768816115601e-02, 5.938147860862002e-02, 6.712547141843697e-02, 7.315618472508867e-02, 7.698637101398070e-02, 7.829964355194252e-02, 7.698637101398070e-02, 7.315618472508868e-02, 6.712547141843697e-02, 5.938147860862003e-02, 5.052768816115601e-02, 4.121749748277349e-02, 3.208466075330589e-02, 2.367919781235187e-02, 1.641655403173896e-02, 1.054583615321984e-02, 6.140246552700078e-03, 3.109782673001019e-03, 1.233293769907379e-03, 2.045080082468671e-04, -3.150057733488439e-04, -6.435871671502849e-04, };
vector <double> c_lpf10h_a = {1.000000000000000e+00, };

Filter f_lpf10h(c_lpf10h_b, c_lpf10h_a);

vector<double> c_lpf4_b = {-1.676812318972605e-03, -5.374936889747954e-04, 2.254940908923396e-03, 4.022274254815428e-03, -1.073502430983471e-04, -9.045704503701428e-03, -1.052619532644138e-02, 5.739018325719546e-03, 2.654003770829400e-02, 1.932369268654869e-02, -2.683398362195290e-02, -6.680566651536425e-02, -2.689580509531039e-02, 1.159324474560186e-01, 2.868022627927465e-01, 3.636286743614999e-01, 2.868022627927465e-01, 1.159324474560186e-01, -2.689580509531039e-02, -6.680566651536426e-02, -2.683398362195291e-02, 1.932369268654870e-02, 2.654003770829402e-02, 5.739018325719549e-03, -1.052619532644138e-02, -9.045704503701428e-03, -1.073502430983470e-04, 4.022274254815429e-03, 2.254940908923395e-03, -5.374936889747954e-04, -1.676812318972605e-03, };
vector <double> c_lpf4_a = {1.000000000000000e+00, };

Filter f_lpf4(c_lpf4_b, c_lpf4_a);

vector<double> c_lpf10_b = {1.530960711199010e-03, 4.310659751765299e-04, -1.889456548691172e-03, -4.446167541609468e-03, -3.877803004174977e-03, 2.888264273604397e-03, 1.315839165131086e-02, 1.665818472124762e-02, 2.830990350722843e-03, -2.611421204951105e-02, -4.845515040504186e-02, -3.288557930240953e-02, 3.796538586827169e-02, 1.478202687871681e-01, 2.491879046693181e-01, 2.903939036868379e-01, 2.491879046693181e-01, 1.478202687871681e-01, 3.796538586827171e-02, -3.288557930240955e-02, -4.845515040504188e-02, -2.611421204951106e-02, 2.830990350722846e-03, 1.665818472124763e-02, 1.315839165131086e-02, 2.888264273604397e-03, -3.877803004174976e-03, -4.446167541609470e-03, -1.889456548691171e-03, 4.310659751765299e-04, 1.530960711199010e-03, };
vector <double> c_lpf10_a = {1.000000000000000e+00, };

Filter f_lpf10(c_lpf10_b, c_lpf10_a);

vector<double> c_sync_b = {4.529500990800284e-03, 5.042565886563957e-03, 6.543687151896889e-03, 8.981720927353037e-03, 1.226825957164825e-02, 1.628097813268541e-02, 2.086834898291218e-02, 2.585553998651212e-02, 3.105126295536169e-02, 3.625529990284258e-02, 4.126640635953664e-02, 4.589027496220054e-02, 4.994723935586487e-02, 5.327940831632746e-02, 5.575694252624885e-02, 5.728322071856454e-02, 5.779868654536129e-02, 5.728322071856454e-02, 5.575694252624885e-02, 5.327940831632746e-02, 4.994723935586488e-02, 4.589027496220054e-02, 4.126640635953666e-02, 3.625529990284259e-02, 3.105126295536169e-02, 2.585553998651212e-02, 2.086834898291218e-02, 1.628097813268542e-02, 1.226825957164825e-02, 8.981720927353037e-03, 6.543687151896896e-03, 5.042565886563960e-03, 4.529500990800284e-03, };
vector <double> c_sync_a = {1.000000000000000e+00, };

Filter f_sync(c_sync_b, c_sync_a);

vector<double> c_dsync_b = {4.529500990800284e-03, 5.042565886563957e-03, 6.543687151896889e-03, 8.981720927353037e-03, 1.226825957164825e-02, 1.628097813268541e-02, 2.086834898291218e-02, 2.585553998651212e-02, 3.105126295536169e-02, 3.625529990284258e-02, 4.126640635953664e-02, 4.589027496220054e-02, 4.994723935586487e-02, 5.327940831632746e-02, 5.575694252624885e-02, 5.728322071856454e-02, 5.779868654536129e-02, 5.728322071856454e-02, 5.575694252624885e-02, 5.327940831632746e-02, 4.994723935586488e-02, 4.589027496220054e-02, 4.126640635953666e-02, 3.625529990284259e-02, 3.105126295536169e-02, 2.585553998651212e-02, 2.086834898291218e-02, 1.628097813268542e-02, 1.226825957164825e-02, 8.981720927353037e-03, 6.543687151896896e-03, 5.042565886563960e-03, 4.529500990800284e-03, };
vector <double> c_dsync_a = {1.000000000000000e+00, };

Filter f_dsync(c_dsync_b, c_dsync_a);

vector<double> c_dsync4_b = {7.303869295435693e-03, 9.373681812569543e-03, 1.536907679358834e-02, 2.471693290630483e-02, 3.651066972938139e-02, 4.959929457148312e-02, 6.270094081265257e-02, 7.452962766411166e-02, 8.392262835864088e-02, 8.995575354480928e-02, 9.203504902204507e-02, 8.995575354480928e-02, 8.392262835864091e-02, 7.452962766411167e-02, 6.270094081265259e-02, 4.959929457148313e-02, 3.651066972938140e-02, 2.471693290630484e-02, 1.536907679358834e-02, 9.373681812569543e-03, 7.303869295435693e-03, };
vector <double> c_dsync4_a = {1.000000000000000e+00, };

Filter f_dsync4(c_dsync4_b, c_dsync4_a);

vector<double> c_dsync10_b = {4.557803338423001e-03, 5.069474325791004e-03, 6.573035815238145e-03, 9.014902485437780e-03, 1.230462007835800e-02, 1.631831041800225e-02, 2.090344220074396e-02, 2.588474191483322e-02, 3.107101346089618e-02, 3.626259841086699e-02, 4.125918284918357e-02, 4.586764245028043e-02, 4.990961545330831e-02, 5.322850359659036e-02, 5.569562346903135e-02, 5.721526423807723e-02, 5.772845098987632e-02, 5.721526423807723e-02, 5.569562346903136e-02, 5.322850359659036e-02, 4.990961545330831e-02, 4.586764245028043e-02, 4.125918284918359e-02, 3.626259841086701e-02, 3.107101346089619e-02, 2.588474191483322e-02, 2.090344220074396e-02, 1.631831041800226e-02, 1.230462007835800e-02, 9.014902485437780e-03, 6.573035815238150e-03, 5.069474325791006e-03, 4.557803338423001e-03, };
vector <double> c_dsync10_a = {1.000000000000000e+00, };

Filter f_dsync10(c_dsync10_b, c_dsync10_a);

vector<double> c_sync4_b = {7.303869295435693e-03, 9.373681812569543e-03, 1.536907679358834e-02, 2.471693290630483e-02, 3.651066972938139e-02, 4.959929457148312e-02, 6.270094081265257e-02, 7.452962766411166e-02, 8.392262835864088e-02, 8.995575354480928e-02, 9.203504902204507e-02, 8.995575354480928e-02, 8.392262835864091e-02, 7.452962766411167e-02, 6.270094081265259e-02, 4.959929457148313e-02, 3.651066972938140e-02, 2.471693290630484e-02, 1.536907679358834e-02, 9.373681812569543e-03, 7.303869295435693e-03, };
vector <double> c_sync4_a = {1.000000000000000e+00, };

Filter f_sync4(c_sync4_b, c_sync4_a);

vector<double> c_sync10_b = {4.557803338423001e-03, 5.069474325791004e-03, 6.573035815238145e-03, 9.014902485437780e-03, 1.230462007835800e-02, 1.631831041800225e-02, 2.090344220074396e-02, 2.588474191483322e-02, 3.107101346089618e-02, 3.626259841086699e-02, 4.125918284918357e-02, 4.586764245028043e-02, 4.990961545330831e-02, 5.322850359659036e-02, 5.569562346903135e-02, 5.721526423807723e-02, 5.772845098987632e-02, 5.721526423807723e-02, 5.569562346903136e-02, 5.322850359659036e-02, 4.990961545330831e-02, 4.586764245028043e-02, 4.125918284918359e-02, 3.626259841086701e-02, 3.107101346089619e-02, 2.588474191483322e-02, 2.090344220074396e-02, 1.631831041800226e-02, 1.230462007835800e-02, 9.014902485437780e-03, 6.573035815238150e-03, 5.069474325791006e-03, 4.557803338423001e-03, };
vector <double> c_sync10_a = {1.000000000000000e+00, };

Filter f_sync10(c_sync10_b, c_sync10_a);

vector<double> c_nr_b = {-1.143846942935882e-04, 3.584105273039791e-03, 1.140000881214164e-02, 1.676582098971625e-02, 7.722211160693353e-04, -5.305059484454877e-02, -1.378551899656667e-01, -2.184063058512996e-01, 7.493807405973140e-01, -2.184063058512996e-01, -1.378551899656667e-01, -5.305059484454879e-02, 7.722211160693354e-04, 1.676582098971625e-02, 1.140000881214164e-02, 3.584105273039794e-03, -1.143846942935882e-04, };
vector <double> c_nr_a = {1.000000000000000e+00, };

Filter f_nr(c_nr_b, c_nr_a);

vector<double> c_nrc_b = {-1.034261478471172e-03, -1.843732736563087e-03, -3.663326015366832e-03, -6.989071125285674e-03, -1.213499908374429e-02, -1.914535709857002e-02, -2.774893589700136e-02, -3.736653927169339e-02, -4.717320203966579e-02, -5.620672685442145e-02, -6.350536190633704e-02, -6.825166884492961e-02, 9.309139809782468e-01, -6.825166884492961e-02, -6.350536190633704e-02, -5.620672685442146e-02, -4.717320203966580e-02, -3.736653927169339e-02, -2.774893589700137e-02, -1.914535709857003e-02, -1.213499908374429e-02, -6.989071125285675e-03, -3.663326015366835e-03, -1.843732736563090e-03, -1.034261478471172e-03, };
vector <double> c_nrc_a = {1.000000000000000e+00, };

Filter f_nrc(c_nrc_b, c_nrc_a);

vector<double> c_colorlp4_b = {4.224940821425686e-03, 7.774815962571446e-03, 1.758159496163114e-02, 3.461179169020320e-02, 5.763509224330938e-02, 8.328571544864401e-02, 1.068234531541468e-01, 1.233862071783184e-01, 1.293527770794995e-01, 1.233862071783184e-01, 1.068234531541468e-01, 8.328571544864405e-02, 5.763509224330939e-02, 3.461179169020320e-02, 1.758159496163114e-02, 7.774815962571453e-03, 4.224940821425686e-03, };
vector <double> c_colorlp4_a = {1.000000000000000e+00, };

Filter f_colorlp4(c_colorlp4_b, c_colorlp4_a);

vector<double> c_colorwlp4_b = {-8.785268914353954e-04, 7.528555009886992e-03, 4.492529862723096e-02, 1.216116946962619e-01, 2.055637761539009e-01, 2.424984048083091e-01, 2.055637761539010e-01, 1.216116946962620e-01, 4.492529862723098e-02, 7.528555009886994e-03, -8.785268914353954e-04, };
vector <double> c_colorwlp4_a = {1.000000000000000e+00, };

Filter f_colorwlp4(c_colorwlp4_b, c_colorwlp4_a);

vector<double> c_colorbp4_b = {3.524083455247116e-02, 5.701405570187424e-07, -2.408398699505458e-01, -7.721391739544891e-07, 4.478385909901386e-01, -7.721391739544892e-07, -2.408398699505458e-01, 5.701405570187425e-07, 3.524083455247116e-02, };
vector <double> c_colorbp4_a = {1.000000000000000e+00, };

Filter f_colorbp4(c_colorbp4_b, c_colorbp4_a);

vector<double> c_colorbp8_b = {1.793619856237312e-02, 1.830493260618777e-02, 2.901791166132613e-07, -5.828484174075743e-02, -1.225780201867041e-01, -1.151386533377725e-01, -3.929884668654460e-07, 1.554887898923649e-01, 2.279322267448763e-01, 1.554887898923649e-01, -3.929884668654461e-07, -1.151386533377726e-01, -1.225780201867041e-01, -5.828484174075742e-02, 2.901791166132614e-07, 1.830493260618778e-02, 1.793619856237312e-02, };
vector <double> c_colorbp8_a = {1.000000000000000e+00, };

Filter f_colorbp8(c_colorbp8_b, c_colorbp8_a);

vector<double> c_audioin_b = {6.264676297181575e-05, 5.011741037745261e-04, 1.754109363210842e-03, 3.508218726421684e-03, 4.385273408027108e-03, 3.508218726421687e-03, 1.754109363210842e-03, 5.011741037745261e-04, 6.264676297181575e-05, };
vector <double> c_audioin_a = {1.000000000000000e+00, -4.296261223770347e+00, 8.605029163253324e+00, -1.030114121932772e+01, 7.988654459506189e+00, -4.084698227805923e+00, 1.338972278884773e+00, -2.564275537013405e-01, 2.190989428180733e-02, };

Filter f_audioin(c_audioin_b, c_audioin_a);

vector<double> c_leftbp_b = {4.350594178170077e-03, 3.343353081524372e-03, -1.073777500952160e-02, 6.809375467894310e-03, 1.325000742922696e-02, -2.883374689763496e-02, 9.021888779772603e-03, 3.827116250507442e-02, -5.470668753938947e-02, 5.023399166322933e-04, 7.476449641552810e-02, -7.362913874573603e-02, -2.256712972745371e-02, 1.081863992377557e-01, -7.307596205518978e-02, -5.219545078331883e-02, 1.217792293188160e-01, -5.219545078331883e-02, -7.307596205518979e-02, 1.081863992377557e-01, -2.256712972745372e-02, -7.362913874573603e-02, 7.476449641552813e-02, 5.023399166322935e-04, -5.470668753938947e-02, 3.827116250507442e-02, 9.021888779772601e-03, -2.883374689763498e-02, 1.325000742922697e-02, 6.809375467894310e-03, -1.073777500952160e-02, 3.343353081524374e-03, 4.350594178170077e-03, };
vector <double> c_leftbp_a = {1.000000000000000e+00, };

Filter f_leftbp(c_leftbp_b, c_leftbp_a);

vector<double> c_rightbp_b = {-3.344787284659096e-04, 5.326122609378982e-03, -1.062063536469220e-02, 1.319272573678146e-02, -7.526868009955771e-03, -9.515227663022496e-03, 3.297088673017457e-02, -4.895470189529476e-02, 4.174697639258265e-02, -5.524633741995795e-03, -4.753368515984027e-02, 9.023945938850934e-02, -9.494734685492431e-02, 5.148656444228708e-02, 2.352675687230025e-02, -9.349039122306163e-02, 1.218736343286970e-01, -9.349039122306163e-02, 2.352675687230025e-02, 5.148656444228708e-02, -9.494734685492433e-02, 9.023945938850934e-02, -4.753368515984029e-02, -5.524633741995797e-03, 4.174697639258265e-02, -4.895470189529476e-02, 3.297088673017456e-02, -9.515227663022503e-03, -7.526868009955772e-03, 1.319272573678146e-02, -1.062063536469221e-02, 5.326122609378985e-03, -3.344787284659096e-04, };
vector <double> c_rightbp_a = {1.000000000000000e+00, };

Filter f_rightbp(c_rightbp_b, c_rightbp_a);

vector<double> c_audiolp_b = {9.018203945583721e-03, 1.302843412812138e-02, 2.442601670674008e-02, 4.154873296589476e-02, 6.182284155984357e-02, 8.216111872091285e-02, 9.944459487809743e-02, 1.110116721698876e-01, 1.150767698498372e-01, 1.110116721698876e-01, 9.944459487809744e-02, 8.216111872091289e-02, 6.182284155984358e-02, 4.154873296589476e-02, 2.442601670674008e-02, 1.302843412812140e-02, 9.018203945583721e-03, };
vector <double> c_audiolp_a = {1.000000000000000e+00, };

Filter f_audiolp(c_audiolp_b, c_audiolp_a);

vector<double> c_audiolp20_b = {1.582326584427475e-03, 1.060583456952443e-03, -7.198540307700431e-04, -3.526708731461865e-03, -5.087593805156031e-03, -1.869066043076291e-03, 6.986103170526893e-03, 1.588766920288095e-02, 1.443730828836575e-02, -3.980136456777393e-03, -3.227210029151829e-02, -4.794657582123650e-02, -2.480328193065671e-02, 4.760265511241622e-02, 1.507766736888626e-01, 2.423732380503912e-01, 2.789975191116594e-01, 2.423732380503912e-01, 1.507766736888626e-01, 4.760265511241622e-02, -2.480328193065672e-02, -4.794657582123650e-02, -3.227210029151831e-02, -3.980136456777395e-03, 1.443730828836575e-02, 1.588766920288095e-02, 6.986103170526893e-03, -1.869066043076293e-03, -5.087593805156033e-03, -3.526708731461865e-03, -7.198540307700439e-04, 1.060583456952443e-03, 1.582326584427475e-03, };
vector <double> c_audiolp20_a = {1.000000000000000e+00, };

Filter f_audiolp20(c_audiolp20_b, c_audiolp20_a);

vector<double> c_a500_48k_b = {-1.594075076043687e-03, -2.316875047321394e-03, -4.366381543402311e-03, -7.459819571988998e-03, -1.113957870309059e-02, -1.484523621957591e-02, -1.800352908393771e-02, -2.012137572599848e-02, 9.807205156831793e-01, -2.012137572599848e-02, -1.800352908393772e-02, -1.484523621957592e-02, -1.113957870309059e-02, -7.459819571988996e-03, -4.366381543402312e-03, -2.316875047321396e-03, -1.594075076043687e-03, };
vector <double> c_a500_48k_a = {1.000000000000000e+00, };

Filter f_a500_48k(c_a500_48k_b, c_a500_48k_a);

vector<double> c_a500_44k_b = {-1.720382225986334e-03, -2.505585658275188e-03, -4.730348153602203e-03, -8.093603282119598e-03, -1.210053119496442e-02, -1.614086472567362e-02, -1.958776236999286e-02, -2.190064570365665e-02, 9.789966491496416e-01, -2.190064570365666e-02, -1.958776236999286e-02, -1.614086472567363e-02, -1.210053119496443e-02, -8.093603282119598e-03, -4.730348153602204e-03, -2.505585658275191e-03, -1.720382225986334e-03, };
vector <double> c_a500_44k_a = {1.000000000000000e+00, };

Filter f_a500_44k(c_a500_44k_b, c_a500_44k_a);

vector<double> c_a40h_48k_b = {-1.333121149734411e-04, -1.916749910304367e-04, -3.578736354901448e-04, -6.066209338338867e-04, -9.000541728243622e-04, -1.193500638256606e-03, -1.442281083933718e-03, -1.608514692682642e-03, 9.984664195028362e-01, -1.608514692682642e-03, -1.442281083933718e-03, -1.193500638256607e-03, -9.000541728243623e-04, -6.066209338338866e-04, -3.578736354901449e-04, -1.916749910304369e-04, -1.333121149734411e-04, };
vector <double> c_a40h_48k_a = {1.000000000000000e+00, };

Filter f_a40h_48k(c_a40h_48k_b, c_a40h_48k_a);

vector<double> c_hilbertr_b = {-1.851851851851851e-02, -1.851851851851858e-02, -1.851851851851844e-02, -1.851851851851872e-02, -1.851851851851852e-02, -1.851851851851849e-02, -1.851851851851853e-02, -1.851851851851849e-02, -1.851851851851843e-02, -1.851851851851853e-02, -1.851851851851844e-02, -1.851851851851846e-02, -1.851851851851794e-02, 4.814814814814815e-01, -1.851851851851872e-02, -1.851851851851850e-02, -1.851851851851857e-02, -1.851851851851854e-02, -1.851851851851870e-02, -1.851851851851853e-02, -1.851851851851857e-02, -1.851851851851865e-02, -1.851851851851852e-02, -1.851851851851849e-02, -1.851851851851857e-02, -1.851851851851850e-02, -1.851851851851852e-02, };
vector <double> c_hilbertr_a = {1.000000000000000e+00, };

Filter f_hilbertr(c_hilbertr_b, c_hilbertr_a);

vector<double> c_hilberti_b = {-1.962848289588819e-02, 1.553888205883857e-02, -2.487468723645290e-02, 1.217982123436036e-02, -3.207501495497922e-02, 9.300349555976783e-03, -4.293075142238721e-02, 6.740189523448193e-03, -6.185615955811687e-02, 4.388969514287131e-03, -1.050237374003280e-01, 2.164504384410190e-03, -3.179506838793675e-01, 0.000000000000000e+00, 3.179506838793673e-01, -2.164504384410416e-03, 1.050237374003280e-01, -4.388969514286931e-03, 6.185615955811677e-02, -6.740189523448237e-03, 4.293075142238729e-02, -9.300349555976842e-03, 3.207501495497922e-02, -1.217982123436019e-02, 2.487468723645292e-02, -1.553888205883851e-02, 1.962848289588827e-02, };
vector <double> c_hilberti_a = {1.000000000000000e+00, };

Filter f_hilberti(c_hilberti_b, c_hilberti_a);

vector<double> c_fmdeemp_b = {4.795408695004655e-05, 7.097070232758687e-05, 1.162983920200813e-04, 2.377538100602406e-04, 4.036970192157422e-04, 7.910534993095139e-04, 1.308086972794372e-03, 2.329168150063381e-03, 3.867050819971179e-03, 6.323290047668001e-03, 1.047733988469226e-02, 1.648258718313019e-02, 2.679862393683207e-02, 4.292534896850254e-02, 6.966728643948848e-02, 1.324241229048471e-01, 2.874090238495433e-01, 1.324241229048468e-01, 6.966728643948851e-02, 4.292534896850245e-02, 2.679862393683206e-02, 1.648258718313015e-02, 1.047733988469226e-02, 6.323290047667920e-03, 3.867050819971209e-03, 2.329168150063344e-03, 1.308086972794367e-03, 7.910534993095119e-04, 4.036970192157484e-04, 2.377538100602358e-04, 1.162983920200774e-04, 7.097070232758928e-05, 4.795408695005012e-05, };
vector <double> c_fmdeemp_a = {1.000000000000000e+00, };

Filter f_fmdeemp(c_fmdeemp_b, c_fmdeemp_a);

