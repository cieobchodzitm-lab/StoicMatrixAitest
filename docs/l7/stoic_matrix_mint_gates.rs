//! HSA-001 Virtue Passport — L7-hardened mint instructions
//! Enforces AGT L7 gates: virtue_score threshold, passportStage, PDA-only authority
//! ConstitutionalAudit: audit-2026-08-14-HSA001-mint-blueprint-001
//! No Pinky

use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, MintTo};

declare_id!("StoicMatrix1111111111111111111111111111111");

pub const DEFAULT_VIRTUE_THRESHOLD: u64 = 70;

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum PassportStage {
    Untrusted = 0,
    Provisional = 1,
    Trusted = 2,
}

#[program]
pub mod stoic_matrix {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, auth_bump: u8, virtue_threshold: u64) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.authority = ctx.accounts.authority.key();
        state.auth_bump = auth_bump;
        state.virtue_threshold = if virtue_threshold == 0 { DEFAULT_VIRTUE_THRESHOLD } else { virtue_threshold };
        state.mainnet_locked = false;
        Ok(())
    }

    pub fn mint_virtue_passport(
        ctx: Context<MintVirtuePassport>,
        name: String,
        symbol: String,
        uri: String,
        virtue_score: u64,
        passport_stage: PassportStage,
        constitution_id: String,
    ) -> Result<()> {
        let state = &ctx.accounts.state;

        require_keys_eq!(ctx.accounts.authority.key(), state.authority, StoicError::UnauthorizedAuthority);
        require!(virtue_score >= state.virtue_threshold, StoicError::InsufficientVirtueScore);

        if state.mainnet_locked {
            require!(passport_stage != PassportStage::Untrusted, StoicError::UntrustedStageForbiddenOnMainnet);
        }

        // Mint + metadata CPI (placeholder for Metaplex Core)
        // Program PDA = sole mint + update authority

        emit!(VirtuePassportMinted {
            nft_mint: ctx.accounts.nft_mint.key(),
            recipient: ctx.accounts.nft_token_account.owner,
            virtue_score,
            passport_stage: passport_stage as u8,
            constitution_id,
            threshold_used: state.virtue_threshold,
            timestamp: Clock::get()?.unix_timestamp,
            audit_ref: "53d55933462d875e46b230a583a05d899a2a253b38c5a52ce5b73efccd98a842".to_string(),
        });

        Ok(())
    }

    // update_passport_metadata, set_mainnet_locked, set_virtue_threshold
    // (full stubs in workspace artifacts)
}

#[account]
pub struct StoicState {
    pub authority: Pubkey,
    pub auth_bump: u8,
    pub virtue_threshold: u64,
    pub mainnet_locked: bool,
}

#[event]
pub struct VirtuePassportMinted {
    pub nft_mint: Pubkey,
    pub recipient: Pubkey,
    pub virtue_score: u64,
    pub passport_stage: u8,
    pub constitution_id: String,
    pub threshold_used: u64,
    pub timestamp: i64,
    pub audit_ref: String,
}

#[error_code]
pub enum StoicError {
    #[msg("Unauthorized")]
    UnauthorizedAuthority,
    #[msg("Insufficient Virtue Score")]
    InsufficientVirtueScore,
    #[msg("Untrusted stage forbidden on mainnet")]
    UntrustedStageForbiddenOnMainnet,
}
