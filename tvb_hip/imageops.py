import mne
import os
import os.path as op
import shutil
import nibabel
import glob, os, tqdm, concurrent.futures, subprocess, nibabel
import epinov_util_JD as eu, subprocess, os, importlib; importlib.reload(eu);
import numpy as np


epinov_data_xfer = '/home/prior/jd_home/code/jd/code_vep/dassault/epinov-data-xfer'

zip_contents = op.join(epinov_data_xfer, 'ready')

# 1) remove the directory named "ready" within the epinov-data-xfer directory
# 2) then loop over all the patients to be transfered and call transfer_patient(pid)
# 3) then create the clinical report for each patient in ~/jd_home/vep_clinical_reports/{pid}.txt
#    and copy it within the directory epinov-data-xfer/{pid}/
# 4) copy also the complete report !!
# 5) then loop over all the patients to be transfered and call copy_patient(pid)
# 6) once all patients have been transfered, create the list of files:
#       cd epinov-data-xfer
#       ls -lR * > 3DS.txt

# 7) finally, create the zip with make_zip.sh


def transfer_patient(pid):
    #print()
    #print()
    #print()
    print('>> 1) check_patient...')
    try:
        check_patient(pid)
    except:
        print('>> 1) check_patient: NOK')
    else:
        print('>> 1) check_patient: OK')
    print()

    print('>> 2) init_patient...')
    try:
       init_patient(pid)
    except:
        print('>> 2) init_patient: NOK')
    else:
        print('>> 2) init_patient: OK')
    print()


    print('>> 3) mask_original...')
    try:
       mask_original(pid)
    except:
        print('>> 3) mask_original: NOK')
    else:
        print('>> 3) mask_original: OK')
    print()


    print('>> 4) mask_original_dwi_AP...')
    try:
       mask_original_dwi_AP(pid)
    except:
        print('>> 4) mask_original_dwi_AP: NOK')
    else:
        print('>> 4) mask_original_dwi_AP: OK')
    print()


    print('>> 5) mask_original_dwi_PA...')
    try:
       mask_original_dwi_PA(pid)
    except:
        print('>> 5) mask_original_dwi_PA: NOK')
    else:
        print('>> 5) mask_original_dwi_PA: OK')
    print()


    print('>> 6) seeg_coords_to_t1...')
    try:
       seeg_coords_to_t1(pid)
    except:
        print('>> 6) seeg_coords_to_t1: NOK')
    else:
        print('>> 6) seeg_coords_to_t1: OK')
    print()


    print('>> 7) convert_vhdrs...')
    try:
       convert_vhdrs(pid)
    except:
        print('>> 7) convert_vhdrs: NOK')
    else:
        print('>> 7) convert_vhdrs: OK')
    print()



def check_patient(pid):
    #print(pid)
    # t1, = find(pid, 'anat', '*_T1w.nii')
    t1, = find(pid, 'anat', '*preop_T1w.nii')
    print(t1)
    ct_fn, = find(pid, 'anat', '*postimp_CT.nii')
    
    # some patients have many run (run-01, run-02, ...) and other dont have any
    # dwi, = find(pid, 'dwi', '*64dir_dir-AP*.nii')
    # dwi, = find(pid, 'dwi', '*64dir_dir-AP_run-01_dwi.nii')
    dwi, = find(pid, 'dwi', '*64dir_dir-AP*dwi.nii')
    print(dwi)
    # bvec, = find(pid, 'dwi', '*AP*bvec*')
    # bvec, = find(pid, 'dwi', '*64dir_dir-AP_run-01_dwi.bvec') # to get rid of b0_dir-AP_run-01_dwi.bvec
    bvec, = find(pid, 'dwi', '*64dir_dir-AP*dwi.bvec') # to get rid of b0_dir-AP_run-01_dwi.bvec
    print(bvec)
    # bval, = find(pid, 'dwi', '*AP*bval*')
    # bval, = find(pid, 'dwi', '*64dir_dir-AP_run-01_dwi.bval') # to get rid of b0_dir-AP_run-01_dwi.bval
    bval, = find(pid, 'dwi', '*64dir_dir-AP*dwi.bval') # to get rid of b0_dir-AP_run-01_dwi.bval
    print(bval)
    sxyz, = find(pid, 'ieeg', '*CT_electrodes.tsv')
    print(sxyz)
    vhdrs = find(pid, 'ieeg', '*.vhdr')
    #print(vhdrs)

    #print()
        
        
def init_patient(pid):
    #print(pid)
    src_dir = op.join('/data', 'vep', pid, 'mri')
    dst_dir = op.join(epinov_data_xfer, pid, 'mri')
    os.makedirs(dst_dir, exist_ok=True)
    for f in ['T1.mgz', 'brainmask.mgz']:
        #print(op.join(src_dir, f), op.join(dst_dir, f))
        shutil.copyfile(op.join(src_dir, f), op.join(dst_dir, f))    
    
    
def ras_ro(img_fn, wd=None):
    wo_ext = img_fn.split('.mgz')[0].split('.nii.gz')[0]
    if wd is not None:
        wo_ext = os.path.join(wd, os.path.basename(wo_ext))
    ras_fn = wo_ext + '.ras.nii.gz'
    ras_ro_fn = wo_ext + '.ras.ro.nii.gz'
    eu.fs('mri_convert', '-rt', 'nearest', '--out_orientation', 'RAS', img_fn, ras_fn)
    eu.fsl('fslreorient2std', ras_fn, ras_ro_fn)
    return ras_ro_fn


def mask_original(pid):
    #orig_t1_fn = f"epinov/sub-{pid}/ses-01/anat/sub-{pid}_ses-01_acq-preop_T1w.nii"
    #fs_t1_fn = f"epinov-data-xfer/{pid}/mri/T1.mgz"
    pid_no_tmp = pid.rstrip('_tmp')
    orig_t1_fn = op.join('/data/epinov', pid, 'ses-01/anat', f'{pid_no_tmp}_ses-01_acq-preop_T1w.nii')
    fs_t1_fn = op.join(epinov_data_xfer, pid, 'mri/T1.mgz')
    # work files
    #wd = f'epinov-data-xfer/{pid}/mri'
    wd = op.join(epinov_data_xfer, pid, 'mri')
    os.makedirs(wd, exist_ok=True)
    fs_bm_fn = f'{wd}/brainmask.mgz'
    fs_bm_in_orig_fn = f'{wd}/bm_in_orig.nii.gz'
    mask_orig_fn = f'{wd}/mask_orig.nii.gz'
    aff_fn = f'{wd}/fs2orig.mat'
    # format images
    orig_t1_ras_ro_fn = ras_ro(orig_t1_fn)
    fs_t1_ras_ro_fn = ras_ro(fs_t1_fn)
    fs_bm_ras_ro_fn = ras_ro(fs_bm_fn)
    # register images
    eu.fsl('flirt',
           '-ref', orig_t1_ras_ro_fn,
           '-in', fs_t1_ras_ro_fn,
           '-omat', aff_fn,
           '-cost', 'mutualinfo',
           '-dof', 12,
           '-searchrz', -180, 180,
           '-searchry', -180, 180,
           '-searchrx', -180, 180,
          )
    # move mask to original space
    eu.fsl('flirt', '-applyxfm', 
           '-in', fs_bm_ras_ro_fn,
           '-ref', orig_t1_ras_ro_fn,
           '-init', aff_fn,
           '-out', fs_bm_in_orig_fn
          )
    # apply mask to original image
    bm_in_orig = nibabel.load(fs_bm_in_orig_fn).get_fdata()
    orig_img = nibabel.load(orig_t1_ras_ro_fn)
    mask_orig_img = nibabel.nifti1.Nifti1Image(
        orig_img.get_fdata() * (bm_in_orig > 0),
        orig_img.affine
    )
    nibabel.save(mask_orig_img, mask_orig_fn)
    

def find(pid, folder, pattern):
    path = os.path.join('/data', 'epinov', f'{pid}', 'ses-01', folder, pattern)
    return glob.glob(path)


def mask_original_dwi(pid, dir='AP'):
    # find files
    #in_dwi_fn, = find(pid, 'dwi', f'*64dir_dir-{dir}_run-01_dwi.nii')
    #bvec, = find(pid, 'dwi', f'*64dir_dir-{dir}_run-01_dwi.bvec')
    #bval, = find(pid, 'dwi', f'*64dir_dir-{dir}_run-01_dwi.bval')
    in_dwi_fn, = find(pid, 'dwi', f'*64dir_dir-{dir}*dwi.nii')
    bvec, = find(pid, 'dwi', f'*64dir_dir-{dir}*dwi.bvec')
    bval, = find(pid, 'dwi', f'*64dir_dir-{dir}*dwi.bval')
    # prep data
    wd = op.join(epinov_data_xfer, pid, f'dwi-{dir}')
    os.makedirs(wd, exist_ok=True)
    dwi_fn = f'{wd}/dwi.mif'
    eu.mrt_bin('mrconvert', '-fslgrad', bvec, bval, in_dwi_fn, dwi_fn)
    # make b0
    b0_fn = f'{wd}/b0.nii.gz'
    eu.mrt_bin('dwiextract', '-force', '-bzero', dwi_fn, b0_fn)
    # registration work files
    fs_t1_fn = op.join(epinov_data_xfer, pid, 'mri/T1.mgz')
    fs_bm_fn = op.join(epinov_data_xfer, pid, 'mri/brainmask.mgz')
    fs_bm_in_orig_fn = op.join(wd, 'bm_in_orig.nii.gz')
    mask_orig_fn = op.join(wd, 'mask_orig.nii.gz')
    aff_fn = op.join(wd, 'fs2orig.mat')
    # format images
    orig_b0_ras_ro_fn = ras_ro(b0_fn)
    fs_t1_ras_ro_fn = ras_ro(fs_t1_fn)
    fs_bm_ras_ro_fn = ras_ro(fs_bm_fn)
    # register images
    eu.fsl('flirt',
           '-ref', orig_b0_ras_ro_fn,
           '-in', fs_t1_ras_ro_fn,
           '-omat', aff_fn,
           '-cost', 'mutualinfo',
           '-dof', 12,
           '-searchrz', -180, 180,
           '-searchry', -180, 180,
           '-searchrx', -180, 180,
          )
    # move mask to original space
    eu.fsl('flirt', '-applyxfm', 
           '-in', fs_bm_ras_ro_fn,
           '-ref', orig_b0_ras_ro_fn,
           '-init', aff_fn,
           '-out', fs_bm_in_orig_fn
          )
    # apply mask to original image
    bm_in_orig = nibabel.load(fs_bm_in_orig_fn).get_fdata()
    orig_img = nibabel.load(in_dwi_fn)
    mask_orig_img = nibabel.nifti1.Nifti1Image(
        orig_img.get_fdata() * (bm_in_orig > 0)[..., None],
        orig_img.affine
    )
    nibabel.save(mask_orig_img, mask_orig_fn)
    
    
def mask_original_dwi_AP(pid):
    mask_original_dwi(pid, dir='AP')
    
    
def mask_original_dwi_PA(pid):
    mask_original_dwi(pid, dir='PA')
    
    
def seeg_coords_to_t1(pid):
    # find files
    t1_fn, = find(pid, 'anat', '*preop_T1w.nii')
    ct_fn, = find(pid, 'anat', '*postimp_CT.nii')
    sxyz_fn, = find(pid, 'ieeg', '*CT_electrodes.tsv')
    # prep data
    wd = op.join(epinov_data_xfer, pid, 'seeg')
    os.makedirs(wd, exist_ok=True)
    # registration work files
    aff_fn = f'{wd}/ct2t1.mat'
    ct_in_t1_fn = f'{wd}/ct_in_t1.nii.gz'
    # format images
    ct_ras_ro_fn = ras_ro(ct_fn, wd=wd)
    t1_ras_ro_fn = ras_ro(t1_fn, wd=wd)
    # register images
    eu.fsl('flirt',
           '-ref', t1_ras_ro_fn,
           '-in', ct_ras_ro_fn,
           '-omat', aff_fn,
           '-out', ct_in_t1_fn,
           '-cost', 'mutualinfo',
           '-dof', 12,
           '-searchrz', -180, 180,
           '-searchry', -180, 180,
           '-searchrx', -180, 180,
          )
    # load gardel output
    seeg = np.genfromtxt(sxyz_fn, names=True, dtype=None, usecols=(0,1,2,3,4))
    seeg_names = [_.decode('ascii') for _ in seeg['name']]
    seeg_ijk = np.array([seeg[k] for k in 'xyz']).T
    # move to real CT space
    ct_aff = nibabel.load(ct_fn).affine
    seeg_xyz = ct_aff.dot(np.c_[seeg_ijk, np.ones(len(seeg_ijk))].T)[:3].T
    # move to real T1 space
    out = eu.fsl('img2imgcoord',
             '-mm',
             '-src', ct_ras_ro_fn,
             '-dest', ct_in_t1_fn,
             '-xfm', aff_fn,
              stdin='\n'.join(['%f %f %f' % tuple(_) for _ in seeg_xyz]))
    t1_seeg_xyz = np.fromstring('\n'.join(out.strip().split('\n')[1:]), sep=' ').reshape((-1, 3))
    # write to file
    t1_seeg_fn = f'{wd}/t1_seeg.xyz'
    with open(t1_seeg_fn, 'w') as fd:
        for name, (x, y, z) in zip(seeg_names, t1_seeg_xyz):
            fd.write('%s %f %f %f\n' % (name, x, y, z))
        
        
def convert_vhdrs(pid):
    vhdrs = find(pid, 'ieeg', '*_task-seizure_*.vhdr')
    wd = op.join(epinov_data_xfer, pid, 'seeg')
    os.makedirs(wd, exist_ok=True)
    for vhdr in vhdrs:
        raw = mne.io.read_raw_brainvision(vhdr)
        fif_fn = vhdr.replace('.vhdr', '-raw.fif')
        raw.save(fif_fn, overwrite=True)
        

def copy_patient(pid):
    print('>> Copy', pid)
    dst = op.join(zip_contents, pid)
    if op.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    shutil.copy(op.join(epinov_data_xfer, pid, 'mri/mask_orig.nii.gz'), f'{dst}/T1.nii.gz')
    shutil.copy(op.join(epinov_data_xfer, pid, 'dwi-AP/mask_orig.nii.gz'), f'{dst}/DWI_AP.nii.gz')
    #bvec, = find(pid, 'dwi', '*64dir_dir-AP_run-01_dwi.bvec')
    #bval, = find(pid, 'dwi', '*64dir_dir-AP_run-01_dwi.bval')
    bvec = find(pid, 'dwi', '*64dir_dir-AP*dwi.bvec')[0]
    bval = find(pid, 'dwi', '*64dir_dir-AP*dwi.bval')[0]
    shutil.copy(bvec, f'{dst}/AP_bvec')
    shutil.copy(bval, f'{dst}/AP_bval')
    #try:
    if pid in ['sub-acda1a7a0c9c']:
        pass
    else:
        shutil.copy(op.join(epinov_data_xfer, pid, 'dwi-PA/mask_orig.nii.gz'), f'{dst}/DWI_PA.nii.gz')
        #bvec, = find(pid, 'dwi', '*64dir_dir-PA_run-01_dwi.bvec')
        #bval, = find(pid, 'dwi', '*64dir_dir-PA_run-01_dwi.bval')
        bvec = find(pid, 'dwi', '*64dir_dir-PA*dwi.bvec')[0]
        bval = find(pid, 'dwi', '*64dir_dir-PA*dwi.bval')[0]
        shutil.copy(bvec, f'{dst}/PA_bvec')
        shutil.copy(bval, f'{dst}/PA_bval')
    #except Exception as e:
    #    print('no PA for', pid, e)
    shutil.copy(op.join(epinov_data_xfer, pid, 'seeg/t1_seeg.xyz'), f'{dst}/t1_seeg_pos.xyz')
    for fif in glob.glob(f'/data/epinov/{pid}/ses-01/ieeg/*seizure*-raw.fif'):
        shutil.copy(fif, f'{dst}/{os.path.basename(fif)}')

    shutil.copy(op.join(epinov_data_xfer, pid, f"{pid.rstrip('_tmp')}.txt"), f"{dst}/{pid.rstrip('_tmp')}.txt")
    # clinical report
    cmd = 'cp '+op.join(epinov_data_xfer, pid, pid.rstrip('_tmp')+'_clinical_report.*')+' '+dst
    #print(cmd)
    os.system(cmd)







